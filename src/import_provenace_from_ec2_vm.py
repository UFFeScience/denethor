import os, time, json
import sys
from pathlib import Path
from denethor.utils import utils as du, file_utils as dfu
from denethor.executor import execution_manager as dem
from denethor.provenance import provenance_importer as dprov
from denethor import constants as const

# Raiz do projeto
project_root = Path(__file__).resolve().parent.parent

# Mudar o diretório atual para a raiz do projeto
os.chdir(project_root)

input_dir = os.path.join(project_root, "resources/data/full_dataset")
metadata_dir = os.path.join(project_root, "resources/logs/aws_ec2")


def main():
    print(">>> Main program started at: ", du.now_str())

    #################################################################
    #
    # !!!! Force execution parameters !!!!
    #
    #################################################################
    PROVIDER = const.AWS_EC2
    MEMORY_LIST = [1024]
    SET_ACTIVE_STEPS = None  # dont override active steps
    INPUT_FILE_LIST = None
    # FILE_COUNT_LIST = [2, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
    FILE_COUNT_LIST = [30, 35, 40, 45, 50]

    #################################################################

    run_metadata_file = "run_metadata_2025-04-24T19_15_17_824163UTC.json"
    


    with open(os.path.join(metadata_dir, run_metadata_file), "r") as f:
        run_metadata = json.load(f)
        METADATA_FILE_LIST = run_metadata["metadata_file_list"]

    for FILE in METADATA_FILE_LIST:
        print(f"Importing {FILE}")

        #read metadata file
        metadata_file = os.path.join(metadata_dir, FILE)
        with open(metadata_file, "r") as f:
            exec_metadata = json.load(f)
        
        workflow_start_time_ms = exec_metadata["workflow_start_time_ms"]
        workflow_end_time_ms = exec_metadata["workflow_end_time_ms"]
        execution_tag = exec_metadata["execution_tag"]
        workflow_runtime_data = exec_metadata["workflow_runtime_data"]

        workflow_steps = exec_metadata["workflow_steps"]
        provider_info = exec_metadata["provider_info"]
        workflow_info = exec_metadata["workflow_info"]
        statistics_info = exec_metadata["statistics_info"]
        env_properties = exec_metadata["env_properties"]

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

        dprov.import_provenance_from_aws(
            execution_tag,
            workflow_start_time_ms,
            workflow_end_time_ms,
            workflow_runtime_data,
            provider_info,
            workflow_info,
            workflow_steps,
            statistics_info,
            env_properties,
        )
        
        
        
        
        
        
        
        
        # for MEMORY in MEMORY_LIST:

        #     du.override_params(
        #         workflow_steps, PROVIDER, MEMORY, INPUT_FILE_LIST, SET_ACTIVE_STEPS
        #     )


    # # Dictionary to store the produced data during the workflow execution
    # runtime_data = {}

    # # caso input_files_path esteja presente, significa que os dados de entrada serão lidos de um diretório
    # data_params = workflow_steps[0].get("data_params")
    # param_in = data_params.get("param_in")
    # param_out = data_params.get("param_out")

    # input_files_path = data_params.get("input_files_path")
    # input_files_list = data_params.get("input_files_list")
    # if input_files_path:
    #     input_files = dfu.list_files(input_files_path, input_files_list)
    #     runtime_data[param_in] = [{"data": f} for f in input_files]

    # # Set the workflow start time in milliseconds
    # # # vm: 2 inputs
    # # workflow_start_time_ms = 1744507705125
    # # workflow_end_time_ms = 1744507706120

    # # # vm: 5 inputs
    # # workflow_start_time_ms = 1744508323830
    # # workflow_end_time_ms = 1744508326433

    # # # vm: 10 inputs
    # workflow_start_time_ms = 1744508418711
    # workflow_end_time_ms = 1744508425055

    # execution_tag = du.generate_execution_tag(workflow_start_time_ms)

    # print(
    #     f"\n>>> Workflow {execution_tag} start time is: {workflow_start_time_ms} ms | {du.convert_ms_to_str(workflow_start_time_ms)}"
    # )
    # print(
    #     f">>> Workflow {execution_tag} end time is: {workflow_end_time_ms} ms | {du.convert_ms_to_str(workflow_end_time_ms)}"
    # )
    # print(
    #     f">>> Workflow {execution_tag} duration: {workflow_end_time_ms - workflow_start_time_ms} ms"
    # )

    # ############################################################
    # #
    # #  Import provenance data
    # #
    # ############################################################

    # dprov.import_provenance_from_aws(
    #     execution_tag,
    #     workflow_start_time_ms,
    #     workflow_end_time_ms,
    #     runtime_data,
    #     provider_info,
    #     workflow_info,
    #     workflow_steps,
    #     statistics_info,
    #     env_properties,
    # )


if __name__ == "__main__":
    main()
