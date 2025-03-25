import os, time, json
from pathlib import Path
from denethor.utils import utils as du, file_utils as dfu
from denethor.executor import execution_manager as dem
from denethor import constants as const

# Raiz do projeto
project_root = Path(__file__).resolve().parent.parent

# Mudar o diretório atual para a raiz do projeto
os.chdir(project_root)

conf_path = os.path.join(project_root, "conf")
# Load JSON files
with open(os.path.join(conf_path, "provider.json"), "r") as f:
    provider_info = json.load(f)

with open(os.path.join(conf_path, "workflow.json"), "r") as f:
    workflow_info = json.load(f)

with open(os.path.join(conf_path, "workflow_steps.json"), "r") as f:
    workflow_steps = json.load(f)

with open(os.path.join(conf_path, "statistics.json"), "r") as f:
    statistics_info = json.load(f)

# Load the environment configuration
env_properties = du.load_properties(os.path.join(conf_path, "env.properties"))

# Dictionary to store the produced data during the workflow execution
runtime_data = {}


def main():

    print(">>> Main program started at: ", du.now_str())


    #################################################################
    #
    # !!!! Force execution parameters !!!!
    #
    #################################################################
    FORCE_ENV = const.AWS_EC2
    FORCE_MEMORY = None

    override_params(FORCE_ENV, FORCE_MEMORY)

    #################################################################

    # Save Workflow Basic Information: Provider, Workflow, Activities, Statistics, Configurations
    # provider_service.get_or_create(provider_info)
    # workflow_service.get_or_create(workflow_info)
    # statistics_service.get_or_create(statistics_info)

    # Set the workflow start time in milliseconds
    workflow_start_time_ms = int(time.time() * 1000)
    workflow_end_time_ms = None

    execution_tag = du.generate_execution_tag(workflow_start_time_ms)

    print(
        f">>> Workflow {execution_tag} start time is: {workflow_start_time_ms} ms | {du.convert_ms_to_str(workflow_start_time_ms)}"
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
        param_in = data_params.get("param_in")
        param_out = data_params.get("param_out")

        # Check if the step is active
        if step.get("active") is False:
            print(f"\n>>> Activity: {activity} is inactive. Skipping...")
            continue

        # Validation of input parameter
        if param_in is None:
            raise ValueError(
                f"Invalid input parameter: {param_in} for activity: {activity}"
            )

        # caso input_files_path esteja presente, significa que os dados de entrada serão lidos de um diretório
        input_files_path = data_params.get("input_files_path")
        input_files_list = data_params.get("input_files_list")
        if input_files_path:
            input_files = dfu.list_files(input_files_path, input_files_list)
            runtime_data[param_in] = [{"data": f} for f in input_files]

        # recuperar os dados  em runtime indicados por 'input_param_name'
        # input_data será uma lista dos dados necessários para a atividade corrente
        input_data = []
        for key, data in runtime_data.items():
            if key == param_in:
                input_data = [item["data"] for item in data]
                break


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
        runtime_data[param_out] = results
        previous_activity = activity

        print(
            f"\n>>> Activity execution of {activity} | Memory: {memory} | Strategy: {strategy} completed."
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

    # if provider_tag != "aws_lambda":
    #     exit(0)

    # dprov.import_provenance_from_aws(
    #     execution_tag,
    #     workflow_start_time_ms,
    #     workflow_end_time_ms,
    #     runtime_data,
    #     workflow_info,
    #     workflow_steps,
    #     statistics_info,
    #     env_properties,
    # )



def override_params(ENV=None, MEMORY=None):
    for step in workflow_steps:
        if ENV:
            step["provider"] = ENV
            print(f"Warning: Overriding environment to {ENV}!")
        if MEMORY:
            step["memory"] = MEMORY
            print(f"Warning: Overriding memory size to {MEMORY}!")


if __name__ == "__main__":
    main()
