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

    metadata_file_list = []  # List to store metadata file names

    #################################################################
    #
    # !!!! Force execution parameters !!!!
    #
    #################################################################
    PROVIDER = const.AWS_EC2
    MEMORY_LIST = [1024]
    SET_ACTIVE_STEPS = None  # dont override active steps
    FILE_COUNT_LIST = []

    FILE_SELECTION_MODE = None

    #################################################################

    # run3
    workflow_input_files_by_count = { 
        "2" : ["ORTHOMCL371", "ORTHOMCL1313"],
        "5" : ["ORTHOMCL458", "ORTHOMCL938", "ORTHOMCL1027", "ORTHOMCL1370", "ORTHOMCL1678"],
        "10" : ["ORTHOMCL424", "ORTHOMCL626", "ORTHOMCL758", "ORTHOMCL763", "ORTHOMCL1043", "ORTHOMCL1100", "ORTHOMCL1146", "ORTHOMCL1370", "ORTHOMCL1809", "ORTHOMCL1869"],
        "15" : ["ORTHOMCL1", "ORTHOMCL358", "ORTHOMCL458", "ORTHOMCL613", "ORTHOMCL818", "ORTHOMCL884", "ORTHOMCL964", "ORTHOMCL968", "ORTHOMCL974", "ORTHOMCL1083", "ORTHOMCL1305", "ORTHOMCL1316", "ORTHOMCL1490", "ORTHOMCL1965", "ORTHOMCL2001"],
        "20" : ["ORTHOMCL364", "ORTHOMCL374", "ORTHOMCL421", "ORTHOMCL424", "ORTHOMCL648", "ORTHOMCL733", "ORTHOMCL835", "ORTHOMCL942", "ORTHOMCL947", "ORTHOMCL965", "ORTHOMCL968", "ORTHOMCL1008", "ORTHOMCL1100", "ORTHOMCL1408", "ORTHOMCL1527", "ORTHOMCL1619", "ORTHOMCL1816", "ORTHOMCL1869", "ORTHOMCL1890", "ORTHOMCL1906"],
        "25" : ["ORTHOMCL337", "ORTHOMCL510", "ORTHOMCL557", "ORTHOMCL588", "ORTHOMCL596", "ORTHOMCL625", "ORTHOMCL652", "ORTHOMCL780", "ORTHOMCL787", "ORTHOMCL790", "ORTHOMCL884", "ORTHOMCL942", "ORTHOMCL983", "ORTHOMCL990", "ORTHOMCL1008", "ORTHOMCL1087", "ORTHOMCL1316", "ORTHOMCL1374", "ORTHOMCL1375", "ORTHOMCL1678", "ORTHOMCL1779", "ORTHOMCL1833", "ORTHOMCL1895", "ORTHOMCL1940", "ORTHOMCL1952"],
        "30" : ["ORTHOMCL256_2", "ORTHOMCL371", "ORTHOMCL524", "ORTHOMCL626", "ORTHOMCL650", "ORTHOMCL659", "ORTHOMCL665", "ORTHOMCL744", "ORTHOMCL780", "ORTHOMCL836", "ORTHOMCL866", "ORTHOMCL877", "ORTHOMCL878", "ORTHOMCL942", "ORTHOMCL948", "ORTHOMCL989", "ORTHOMCL1002", "ORTHOMCL1043", "ORTHOMCL1127", "ORTHOMCL1129", "ORTHOMCL1166", "ORTHOMCL1311", "ORTHOMCL1352", "ORTHOMCL1480", "ORTHOMCL1677", "ORTHOMCL1686", "ORTHOMCL1882", "ORTHOMCL1915", "ORTHOMCL1952", "ORTHOMCL1985"],
        "35" : ["ORTHOMCL337", "ORTHOMCL358", "ORTHOMCL364", "ORTHOMCL465", "ORTHOMCL515", "ORTHOMCL524", "ORTHOMCL609", "ORTHOMCL625", "ORTHOMCL626", "ORTHOMCL721", "ORTHOMCL733", "ORTHOMCL741", "ORTHOMCL757", "ORTHOMCL787", "ORTHOMCL790", "ORTHOMCL818", "ORTHOMCL830", "ORTHOMCL841", "ORTHOMCL877", "ORTHOMCL884", "ORTHOMCL1021", "ORTHOMCL1023", "ORTHOMCL1029", "ORTHOMCL1039", "ORTHOMCL1100", "ORTHOMCL1104", "ORTHOMCL1518", "ORTHOMCL1780", "ORTHOMCL1788", "ORTHOMCL1795", "ORTHOMCL1833", "ORTHOMCL1861", "ORTHOMCL1909", "ORTHOMCL1916", "ORTHOMCL1954"],
        "40" : ["ORTHOMCL320", "ORTHOMCL337", "ORTHOMCL358", "ORTHOMCL537", "ORTHOMCL557", "ORTHOMCL588", "ORTHOMCL592", "ORTHOMCL613", "ORTHOMCL741", "ORTHOMCL746", "ORTHOMCL748", "ORTHOMCL750", "ORTHOMCL818", "ORTHOMCL853", "ORTHOMCL938", "ORTHOMCL943", "ORTHOMCL968", "ORTHOMCL974", "ORTHOMCL1002", "ORTHOMCL1007", "ORTHOMCL1008", "ORTHOMCL1009", "ORTHOMCL1027", "ORTHOMCL1083", "ORTHOMCL1113", "ORTHOMCL1125", "ORTHOMCL1129", "ORTHOMCL1135", "ORTHOMCL1136", "ORTHOMCL1305", "ORTHOMCL1334", "ORTHOMCL1359", "ORTHOMCL1378", "ORTHOMCL1385", "ORTHOMCL1403", "ORTHOMCL1518", "ORTHOMCL1788", "ORTHOMCL1984", "ORTHOMCL1997", "ORTHOMCL2033"],
        "45" : ["ORTHOMCL1", "ORTHOMCL256_2", "ORTHOMCL320", "ORTHOMCL371", "ORTHOMCL510", "ORTHOMCL617", "ORTHOMCL652", "ORTHOMCL721", "ORTHOMCL744", "ORTHOMCL746", "ORTHOMCL763", "ORTHOMCL830", "ORTHOMCL854", "ORTHOMCL875", "ORTHOMCL884", "ORTHOMCL885", "ORTHOMCL938", "ORTHOMCL964", "ORTHOMCL965", "ORTHOMCL974", "ORTHOMCL1005", "ORTHOMCL1021", "ORTHOMCL1033", "ORTHOMCL1034", "ORTHOMCL1042", "ORTHOMCL1087", "ORTHOMCL1092", "ORTHOMCL1125", "ORTHOMCL1126", "ORTHOMCL1136", "ORTHOMCL1147", "ORTHOMCL1166", "ORTHOMCL1305", "ORTHOMCL1311", "ORTHOMCL1352", "ORTHOMCL1363", "ORTHOMCL1408", "ORTHOMCL1410", "ORTHOMCL1619", "ORTHOMCL1833", "ORTHOMCL1916", "ORTHOMCL1940", "ORTHOMCL1958", "ORTHOMCL1984", "ORTHOMCL2001"],
        "50" : ["ORTHOMCL364", "ORTHOMCL371", "ORTHOMCL374", "ORTHOMCL524", "ORTHOMCL537", "ORTHOMCL557", "ORTHOMCL617", "ORTHOMCL650", "ORTHOMCL667", "ORTHOMCL680", "ORTHOMCL721", "ORTHOMCL733", "ORTHOMCL741", "ORTHOMCL750", "ORTHOMCL787", "ORTHOMCL818", "ORTHOMCL833", "ORTHOMCL835", "ORTHOMCL836", "ORTHOMCL838", "ORTHOMCL841", "ORTHOMCL878", "ORTHOMCL888", "ORTHOMCL943", "ORTHOMCL964", "ORTHOMCL988", "ORTHOMCL1009", "ORTHOMCL1029", "ORTHOMCL1034", "ORTHOMCL1039", "ORTHOMCL1127", "ORTHOMCL1166", "ORTHOMCL1311", "ORTHOMCL1316", "ORTHOMCL1352", "ORTHOMCL1359", "ORTHOMCL1378", "ORTHOMCL1385", "ORTHOMCL1410", "ORTHOMCL1464", "ORTHOMCL1518", "ORTHOMCL1619", "ORTHOMCL1706", "ORTHOMCL1779", "ORTHOMCL1788", "ORTHOMCL1813", "ORTHOMCL1875", "ORTHOMCL1915", "ORTHOMCL1985", "ORTHOMCL2020"] 
    }

    for n_files, file_list in workflow_input_files_by_count.items():

        print(f"Executing with {n_files} files: {file_list}")

        for memory in MEMORY_LIST:

            override_params(
                workflow_steps, PROVIDER, memory, file_list, SET_ACTIVE_STEPS
            )

            ##
            ## Execute the workflow
            ##
            (
                execution_tag,
                workflow_start_time_ms,
                workflow_end_time_ms,
                workflow_runtime_data,
            ) = dexec.execute_workflow(
                workflow_steps,
                env_properties,
            )

            # Write execution metadata and append the filename to the list
            metadata_file = write_execution_metadata_file(
                execution_tag,
                n_files,
                memory,
                workflow_start_time_ms,
                workflow_end_time_ms,
                workflow_runtime_data,
                workflow_steps,
                provider_info,
                workflow_info,
                statistics_info,
                env_properties,
            )

            metadata_file_list.append(metadata_file)

            #
            # Import provenance data
            #
            # dprov.import_provenance_from_aws(
            #     execution_tag,
            #     workflow_start_time_ms,
            #     workflow_end_time_ms,
            #     workflow_runtime_data,
            #     provider_info,
            #     workflow_info,
            #     workflow_steps,
            #     statistics_info,
            #     env_properties,
            # )
    
    run_end_time = timeit.default_timer()
    run_duration = run_end_time - run_start_time
    run_end_datetime = du.now_str()

    print("\n\n>>> Main program finished at: ", run_end_datetime)
    print(
        f">>> Total execution time: {int(run_duration // 60)} minutes and {int(run_duration % 60)} seconds"
    )

    # Save run metadata to a JSON file
    run_metadata_file = write_run_metadata_file(
        run_start_datetime,
        run_end_datetime,
        run_duration,
        workflow_info,
        PROVIDER,
        MEMORY_LIST,
        SET_ACTIVE_STEPS,
        FILE_SELECTION_MODE,
        FILE_COUNT_LIST,
        workflow_input_files_by_count,
        metadata_file_list,
        local_path=os.path.dirname(os.path.abspath(__file__)),
    )

    print(f"Metadata and execution parameters saved to: {run_metadata_file}")


if __name__ == "__main__":
    main()
