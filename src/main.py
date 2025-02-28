import os, time, json
from pathlib import Path
from denethor import environment as denv
from denethor.core.service import *
from denethor.utils import utils as du, file_utils as dfu
from denethor.executor import execution_manager as dem
import denethor.provenance.provenance_importer as dprov

# FORCE_ENV = denv.LOCAL
FORCE_ENV = ""
FORCE_MEMORY = 256

# Raiz do projeto
project_root = Path(__file__).resolve().parent.parent

conf_path = os.path.join(project_root, "conf")
# Load JSON files
with open(os.path.join(conf_path, "provider.json"), "r") as f:
    provider_info = json.load(f)

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

    # Save Workflow Basic Information: Provider, Workflow, Activities, Statistics, Configurations
    providers_db = provider_service.get_or_create(provider_info)
    workflow_db = workflow_service.get_or_create(workflow_info)
    statistics_db = statistics_service.get_or_create(statistics_info)

    # Set the workflow start time in milliseconds
    workflow_start_time_ms = int(time.time() * 1000)
    workflow_end_time_ms = None

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

    execution_tag = du.generate_execution_tag(workflow_start_time_ms)

    print(">>> Main program started at: ", du.now_str())
    print(">>> Workflow start time is (ms):  ", workflow_start_time_ms)
    print(
        ">>> Workflow start time is (str): ",
        du.convert_ms_to_str(workflow_start_time_ms),
    )
    print(">>> Execution TAG: ", execution_tag)
    print(">>> Working directory: ", os.getcwd())

    previous_activity = None

    # For each step in the workflow
    for step in workflow_steps:

        activity = step.get("activity")
        provider_tag = step.get("provider")
        memory = step.get("memory")
        strategy = step.get("strategy")
        data_params = step.get("data_params")

        if FORCE_ENV:
            provider_tag = FORCE_ENV

        if FORCE_MEMORY:
            memory = FORCE_MEMORY

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
            execution_tag,
            provider_tag,
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

        print(
            f"\n>>> Activity {activity} | Memory: {memory} | Strategy: {strategy} completed."
        )

    workflow_end_time_ms = int(time.time() * 1000)

    print(
        f"\n>>> Workflow {execution_tag} start time is: {workflow_start_time_ms} ms | {du.convert_ms_to_str(workflow_start_time_ms)}"
    )
    print(
        f">>> Workflow {execution_tag} end time is: {workflow_end_time_ms} ms | {du.convert_ms_to_str(workflow_end_time_ms)}"
    )
    print(
        f">>> Workflow {execution_tag} duration: {workflow_end_time_ms - workflow_start_time_ms} ms"
    )

    ############################################################
    #
    #  Import provenance data
    #
    ############################################################

    sleep_time = 5
    print(
        f"\n>>> Sleeping for {sleep_time} seconds before importing provenance data..."
    )
    time.sleep(sleep_time)

    prov_start_time_ms = int(time.time() * 1000)
    prov_end_time_ms = None

    print(
        f"\n>>> Provenance import start time is: {prov_start_time_ms} ms | {du.convert_ms_to_str(prov_start_time_ms)}"
    )

    if provider_tag != "aws_lambda":
        exit(0)

    workflow_execution_service.create(
        workflow=workflow_db,
        execution_tag=execution_tag,
        start_time_ms=workflow_start_time_ms,
        end_time_ms=workflow_end_time_ms,
        runtime_data=workflow_runtime_data,
        info="",
    )

    # For each step in the workflow
    for step in workflow_steps:

        # Check if the step is active
        if step.get("active") is False:
            print(f"\n>>> Activity: {activity} is inactive. Skipping...")
            continue

        activity = step.get("activity")
        memory = step.get("memory")

        if FORCE_MEMORY:
            memory = FORCE_MEMORY

        log_path = env_properties.get("provenance").get("log.path")
        log_file_name = env_properties.get("provenance").get("log.file")

        log_path = log_path.replace("[provider_tag]", provider_tag)
        log_file_name = log_file_name.replace("[execution_id]", execution_tag)
        log_file_name = log_file_name.replace("[activity_name]", activity)

        log_file = os.path.join(log_path, log_file_name)

        dprov.import_provenance_from_aws(
            execution_tag,
            activity,
            memory,
            workflow_start_time_ms,
            workflow_end_time_ms,
            log_file,
            workflow_info,
            statistics_info,
        )

    prov_end_time_ms = int(time.time() * 1000)

    print(
        f">>> Provenance import start time: {du.convert_ms_to_str(prov_start_time_ms)}"
    )

    print(f">>> Provenance import end time: {du.convert_ms_to_str(prov_end_time_ms)}")

    print(f">>> Provenance import duration: {prov_end_time_ms - prov_start_time_ms} ms")


if __name__ == "__main__":
    main()
