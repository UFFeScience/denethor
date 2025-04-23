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

conf_path = os.path.join(project_root, "conf")
# Load JSON files
with open(os.path.join(conf_path, "provider.json"), "r") as f:
    provider_info = json.load(f)

with open(os.path.join(conf_path, "workflow.json"), "r") as f:
    workflow_info = json.load(f)

# with open(os.path.join(conf_path, "workflow_steps.json"), "r") as f:
#     workflow_steps = json.load(f)

with open(os.path.join(conf_path, "statistics.json"), "r") as f:
    statistics_info = json.load(f)

# Load the environment configuration
# env_properties = du.load_properties(os.path.join(conf_path, "env.properties"))

# List of files to be processed
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

    # file_count = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    # file_count = 50

    #run1
    # METADATA_FILE_LIST = [
    #     "wetag_1745013809114_002_files__1024_memory.json",
    #     "wetag_1745014054593_005_files__1024_memory.json",
    #     "wetag_1745014057207_010_files__1024_memory.json",
    #     "wetag_1745014063276_015_files__1024_memory.json",
    #     "wetag_1745014073730_020_files__1024_memory.json",
    #     "wetag_1745014088923_025_files__1024_memory.json",
    #     "wetag_1745014109475_030_files__1024_memory.json",
    #     "wetag_1745014136382_035_files__1024_memory.json",
    #     "wetag_1745014169990_040_files__1024_memory.json",
    #     "wetag_1745014211149_045_files__1024_memory.json",
    #     "wetag_1745014259016_050_files__1024_memory.json",
    # ]

    #run2
    METADATA_FILE_LIST = [
        "wetag_1745338482662_002_files__1024_memory.json", 
        "wetag_1745338483556_005_files__1024_memory.json", 
        "wetag_1745338485406_010_files__1024_memory.json", 
        "wetag_1745338489322_015_files__1024_memory.json", 
        "wetag_1745338495958_020_files__1024_memory.json", 
        "wetag_1745338504859_025_files__1024_memory.json", 
        "wetag_1745338516583_030_files__1024_memory.json", 
        "wetag_1745338531891_035_files__1024_memory.json", 
        "wetag_1745338550578_040_files__1024_memory.json", 
        "wetag_1745338573132_045_files__1024_memory.json", 
        "wetag_1745338599911_050_files__1024_memory.json", 
    ]
    #################################################################

    for FILE in METADATA_FILE_LIST:
        print(f"Importing {FILE}")

        #read metadata file
        metadata_file = os.path.join(metadata_dir, FILE)
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        
        INPUT_FILE_LIST = [file["data"] for file in metadata["runtime_data"]["input_files"]]

        
        workflow_start_time_ms = metadata["workflow_start_time_ms"]
        workflow_end_time_ms = metadata["workflow_end_time_ms"]
        execution_tag = metadata["execution_tag"]
        runtime_data = metadata["runtime_data"]

        workflow_steps = metadata["workflow_steps"]
        env_properties = metadata["env_properties"]

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
            runtime_data,
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
