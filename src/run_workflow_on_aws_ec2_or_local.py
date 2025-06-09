import os, sys, timeit, json
from pathlib import Path
from denethor import constants as const
from denethor.executor import workflow_executor as dexec
from denethor.utils import utils as du, file_utils as dfu
from run_workflow_utils import *
# from denethor.core.service import *
# from denethor.provenance import provenance_importer as dprov

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

# List of files to be processed
input_dir = os.path.join(project_root, "resources/data/full_dataset")


def main():

    run_start_time = timeit.default_timer()
    run_start_datetime = du.now_str()

    print(">>> Main program started at: ", run_start_datetime)
    

    #################################################################
    #
    # Configure execution parameters
    #
    #################################################################

    PROVIDER = const.AWS_EC2  # or const.AWS_EC2
    MEMORY_LIST = [1024]
    ACTIVE_STEPS = None  # None -> dont update active steps
    FILE_COUNT_LIST = []
    FILE_SELECTION_MODE = ""  #  "first" or "random"

    METADATA_DIR = "resources/logs/aws_lambda"
    
    # Recebe o nome do arquivo como parâmetro, ou usa valor padrão
    if len(sys.argv) > 1:
        INPUT_METADATA_FILE = sys.argv[1]
    else:
        INPUT_METADATA_FILE = "run_metadata_2025-06-06T16_28_00UTC.json"

    workflow_input_files_by_count = {}

    run_metadata_file = setup_metadata_json_file(
        run_start_datetime, env_properties, PROVIDER
    )
    #################################################################

    
    #
    # OPÇÃO 1: Executar o workflow baseado em metadados de execuções pré-existentes
    #
    # Se METADATA_DIR e INPUT_METADATA_FILE estiverem definidos, carregue o arquivo JSON de metadados
    # A execução do workflow será baseada nesses metadados, em especial na lista de arquivos de entrada
    if METADATA_DIR and INPUT_METADATA_FILE:
    
        with open(os.path.join(METADATA_DIR, INPUT_METADATA_FILE), "r") as f:
            run_metadata = json.load(f)
            
            MEMORY_LIST = [1024] # O valor de memória não é fixo para o AWS EC2 ou execução local
            ACTIVE_STEPS = run_metadata["run_details"]["set_active_steps"]
            FILE_COUNT_LIST = run_metadata["run_details"]["file_count_list"]
            FILE_SELECTION_MODE = "from: " + INPUT_METADATA_FILE
            workflow_input_files_by_count = run_metadata["run_details"]["workflow_input_files_by_count"]

    #
    # OPÇÃO 2: Executar o workflow baseado em configurações definidas manualmente
    #
    else:

        MEMORY_LIST = [1024]
        ACTIVE_STEPS = None  # dont update active steps
        FILE_COUNT_LIST = [2]
        FILE_SELECTION_MODE = None  #  "first" or "random"

        #
        # OPÇÃO 2.1: selecionar arquivos de entrada para o workflow baseado em critérios definidos
        #
        # # workflow_input_files_by_count = select_input_files_for_workflow(
        #     FILE_COUNT_LIST, FILE_SELECTION_MODE, input_dir
        # )

        #
        # OPÇÃO 2.2: definir manualmente os arquivos de entrada para o workflow
        #
        # workflow_input_files_by_count = { 
        #     "2" : ["ORTHOMCL371", "ORTHOMCL1313"],
        #     "5" : ["ORTHOMCL458", "ORTHOMCL938", "ORTHOMCL1027", "ORTHOMCL1370", "ORTHOMCL1678"],
        #     #.....
        # }
    
    

    for n_files, file_list in workflow_input_files_by_count.items():

        print(f"Executing with {n_files} files: {file_list}")

        for memory in MEMORY_LIST:

            update_workflow_step_parameters(
                workflow_steps, PROVIDER, memory, file_list, ACTIVE_STEPS
            )

            execution_tag = None
            workflow_start_time_ms = None
            workflow_end_time_ms = None
            workflow_runtime_data = None
            error = None

            ##  Execute the workflow ##
            try:
                (
                    execution_tag,
                    workflow_start_time_ms,
                    workflow_end_time_ms,
                    workflow_runtime_data,
                ) = dexec.execute_workflow(
                    workflow_steps,
                    env_properties,
                )
            except Exception as e:
                print(f"Error during workflow execution: {e}")
                error = e

            # Append execution metadata to the aggregated JSON file
            append_execution_metadata(
                run_metadata_file,
                execution_tag,
                n_files,
                memory,
                workflow_start_time_ms,
                workflow_end_time_ms,
                workflow_runtime_data,
                workflow_steps,
                errors=[error] if error else [],
            )

    run_end_time = timeit.default_timer()
    run_duration = run_end_time - run_start_time
    run_end_datetime = du.now_str()

    print("\n\n>>> Main program finished at: ", run_end_datetime)
    print(
        f">>> Total execution time: {int(run_duration // 60)} minutes and {int(run_duration % 60)} seconds"
    )

    # Append overall run metadata to the aggregated JSON file
    append_run_metadata(
        run_metadata_file,
        run_start_datetime,
        run_end_datetime,
        run_duration,
        workflow_info.get("workflow_name"),
        PROVIDER,
        MEMORY_LIST,
        ACTIVE_STEPS,
        FILE_SELECTION_MODE,
        FILE_COUNT_LIST,
        workflow_input_files_by_count,
        provider_info,
        workflow_info,
        statistics_info,
        env_properties,
    )

    print(f"Metadata and execution parameters saved to: {run_metadata_file}")


if __name__ == "__main__":
    main()
