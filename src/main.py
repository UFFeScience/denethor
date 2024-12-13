import os, time, json
from pathlib import Path
from denethor import environment as denv
from denethor.utils import utils as du, file_utils as dfu
from denethor.executor import execution_manager as dem
import denethor.provenance.provenance_importer as dprov

# FORCE_ENV = denv.LOCAL
FORCE_ENV = ""

# Raiz do projeto
project_root = Path(__file__).resolve().parent.parent

conf_path = os.path.join(project_root, "conf")
# Load JSON files
with open(os.path.join(conf_path, "provider.json"), "r") as f:
    provider = json.load(f)

with open(os.path.join(conf_path, "workflow.json"), "r") as f:
    workflow_info = json.load(f)

with open(os.path.join(conf_path, "workflow_execution.json"), "r") as f:
    workflow_steps = json.load(f)

with open(os.path.join(conf_path, "statistics.json"), "r") as f:
    statistics_info = json.load(f)

# Load the environment configuration
env_properties = du.load_properties(os.path.join(conf_path, "env.properties"))

# Dictionary to store the produced data during the workflow execution
workflow_runtime_data = {}


def main():

    # Set the workflow start time in milliseconds
    start_time_ms = int(time.time() * 1000)
    end_time_ms = None

    ########################################################################
    # FOR LOCAL TESTING!!!!
    # Comment the following lines to run the workflow as usual
    ########################################################################

    # from datetime import datetime, timezone

    # # Define the start and end time parameters for log retrieval in aws cloudwatch

    # BRAZIL_TZ = "-03:00"
    # UTC_TZ = "-00:00"
    # start_time_human = "2024-10-25T16:07:57" + UTC_TZ #005 nova config
    # end_time_human   = "2024-10-25T16:08:35" + UTC_TZ

    # # Convert the human-readable time to milliseconds
    # start_time_ms = du.convert_str_to_ms(start_time_human)
    # end_time_ms = du.convert_str_to_ms(end_time_human)

    # # Adds a margin of 10 seconds before and after the interval to ensure that all logs are captured
    # start_time_ms -= 10000
    # end_time_ms += 10000

    # # execution_id = du.generate_workflow_execution_id(start_time_ms)
    # # execution_env = du.get_env_config_by_name("local", env_configs)
    # # import denethor.utils.log_handler as dlh
    # # logger = dlh.get_logger(execution_id, execution_env)
    # # du.log_env_info(execution_env, logger)

    # # Setting the active steps for testing
    # # ["tree_constructor", "subtree_constructor", "maf_database_creator", "maf_database_aggregator"]
    # action = "import_provenance"
    # activities = ["tree_constructor", "subtree_constructor", "maf_database_creator", "maf_database_aggregator"]
    # # activities = ["maf_database_aggregator"]

    # for step in workflow_steps:
    #     if step['action'] == action and step['activity'] in activities:
    #         step['active'] = True
    #     else:
    #         step['active'] = False

    ########################################################################

    execution_id = du.generate_workflow_execution_id(start_time_ms)

    print(">>>>>>> Main program started at: ", du.now_str())
    print(">>>>>>> Workflow start time is (ms):  ", start_time_ms)
    print(">>>>>>> Workflow start time is (str): ", du.convert_ms_to_str(start_time_ms))
    print(">>>>>>> Execution ID: ", execution_id)
    print(">>>>>>> Working directory: ", os.getcwd())

    previous_activity = None

    # For each step in the workflow
    for step in workflow_steps:

        activity = step.get("activity")
        provider_code = step.get("provider")
        memory = step.get("memory")
        strategy = step.get("strategy")
        data_params = step.get("data_params")

        if FORCE_ENV:
            provider_code = FORCE_ENV

        # Check if the step is active
        if step.get("active") is False:
            print(f"\n>>> Activity: {activity} is inactive. Skipping...")
            continue

        # Check if the strategy is valid
        if strategy != "for_each_input" and strategy != "for_all_inputs":
            raise ValueError(f"Invalid strategy: {strategy} at activity: {activity}")

        input_param_name = None
        output_param_name = None
        if data_params:
            input_dir = data_params.get("input_dir")
            input_param_name = data_params.get("input_param")
            output_param_name = data_params.get("output_param")

        # Validation of input parameter
        if input_param_name is None:
            raise ValueError(
                f"Invalid input parameter: {input_param_name} for activity: {activity}"
            )

        # caso input_dir esteja presente, significa que os dados de entrada serão lidos de um diretório
        if input_dir:
            input_files = dfu.list_all_files(os.path.join(project_root, input_dir))
            workflow_runtime_data[input_param_name] = [{"data": f} for f in input_files]

        # recuperar os dados  em runtime indicados por 'input_param_name'
        # input_data será uma lista dos dados necessários para a atividade corrente
        input_data = []
        for key, data in workflow_runtime_data.items():
            if key == input_param_name:
                input_data = [item["data"] for item in data]
                break

        # Validation of input data
        if input_data is None:
            raise ValueError(
                f"Invalid input data: {input_data} for data_params: {data_params} at activity: {activity}"
            )

        # Execute the activity
        results = dem.execute_activity(
            execution_id,
            provider_code,
            strategy,
            activity,
            previous_activity,
            memory,
            input_data,
            env_properties,
        )

        # Save the produced data in the dictionary
        workflow_runtime_data[output_param_name] = results
        previous_activity = activity

        print(f"\n>>> {activity} | Memory: {memory} | Strategy: {strategy} completed.")

    end_time_ms = int(time.time() * 1000)

    print(">>>>>>> Workflow end time is (ms):  ", end_time_ms)
    print(">>>>>>> Workflow end time is (str): ", du.convert_ms_to_str(end_time_ms))
    print(
        f"******* Workflow execution {execution_id} finished at: {du.now_str()} *******"
    )

    #################################
    #  Import provenance data
    #################################

    # # Mesmo que o ambiente de execução seja local, é necessário obter as informações de log da AWS
    # # com isso, tempo que pegar o environment_params da AWS
    # aws_env = du.get_env_params_by_name(denv.AWS_LAMBDA, env_params)
    
    print(f"******* Provenance import started at: {du.now_str()} *******")

    if provider_code != "aws_lambda":
        exit(0)

    log_path = env_properties.get("provenance").get("log.path")
    log_file_name = env_properties.get("provenance").get("log.file")
    log_file_name = log_file_name.replace("[execution_id]", execution_id).replace(
        "[activity_name]", activity
    )
    log_file = os.path.join(log_path, log_file_name)

    # For each step in the workflow
    for step in workflow_steps:

        activity = step.get("activity")
        providers_info = step.get("execution_env")
        memory = step.get("memory")
        env_properties.get()

        dprov.import_provenance_from_aws(
            execution_id,
            activity,
            memory,
            start_time_ms,
            end_time_ms,
            log_file,
            providers_info,
            workflow_info,
            statistics_info,
        )

    print(f"******* Provenance import finished at: {du.now_str()} *******")


if __name__ == "__main__":
    main()
