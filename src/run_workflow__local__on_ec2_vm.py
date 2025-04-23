import os, time, json
import sys
from pathlib import Path
from denethor.utils import utils as du, file_utils as dfu
from denethor.executor import execution_manager as dem
from denethor.executor import workflow_executor as dexec

# from denethor.provenance import provenance_importer as dprov
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

# List of files to be processed
input_dir = os.path.join(project_root, "resources/data/full_dataset")

# Dictionary to store the produced data during the workflow execution
runtime_data = {}


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

    # file_count = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    # file_count = 50

    #run2
    INPUT_FILE_DICT = {
        "2": ["ORTHOMCL787", "ORTHOMCL1861"],
        "5": ["ORTHOMCL441", "ORTHOMCL625", "ORTHOMCL888", "ORTHOMCL916", "ORTHOMCL1305"],
        "10": ["ORTHOMCL537", "ORTHOMCL581", "ORTHOMCL755", "ORTHOMCL833", "ORTHOMCL866", "ORTHOMCL989", "ORTHOMCL1005", "ORTHOMCL1408", "ORTHOMCL1491", "ORTHOMCL1541"],
        "15": ["ORTHOMCL364", "ORTHOMCL374", "ORTHOMCL441", "ORTHOMCL510", "ORTHOMCL726", "ORTHOMCL989", "ORTHOMCL1008", "ORTHOMCL1038", "ORTHOMCL1136", "ORTHOMCL1378", "ORTHOMCL1813", "ORTHOMCL1890", "ORTHOMCL1915", "ORTHOMCL1965", "ORTHOMCL1996"],
        "20": ["ORTHOMCL1", "ORTHOMCL424", "ORTHOMCL613", "ORTHOMCL830", "ORTHOMCL836", "ORTHOMCL854", "ORTHOMCL888", "ORTHOMCL942", "ORTHOMCL964", "ORTHOMCL983", "ORTHOMCL988", "ORTHOMCL1021", "ORTHOMCL1113", "ORTHOMCL1131", "ORTHOMCL1166", "ORTHOMCL1305", "ORTHOMCL1378", "ORTHOMCL1464", "ORTHOMCL1861", "ORTHOMCL1997"],
        "25": ["ORTHOMCL515", "ORTHOMCL534", "ORTHOMCL581", "ORTHOMCL744", "ORTHOMCL877", "ORTHOMCL884", "ORTHOMCL964", "ORTHOMCL1000", "ORTHOMCL1005", "ORTHOMCL1008", "ORTHOMCL1009", "ORTHOMCL1039", "ORTHOMCL1074", "ORTHOMCL1125", "ORTHOMCL1129", "ORTHOMCL1136", "ORTHOMCL1147", "ORTHOMCL1311", "ORTHOMCL1491", "ORTHOMCL1677", "ORTHOMCL1678", "ORTHOMCL1762", "ORTHOMCL1772", "ORTHOMCL1977", "ORTHOMCL2001"],
        "30": ["ORTHOMCL1", "ORTHOMCL364", "ORTHOMCL465", "ORTHOMCL510", "ORTHOMCL617", "ORTHOMCL641", "ORTHOMCL659", "ORTHOMCL758", "ORTHOMCL763", "ORTHOMCL854", "ORTHOMCL884", "ORTHOMCL908", "ORTHOMCL943", "ORTHOMCL964", "ORTHOMCL1003", "ORTHOMCL1005", "ORTHOMCL1008", "ORTHOMCL1033", "ORTHOMCL1042", "ORTHOMCL1129", "ORTHOMCL1305", "ORTHOMCL1314", "ORTHOMCL1385", "ORTHOMCL1403", "ORTHOMCL1442", "ORTHOMCL1678", "ORTHOMCL1770", "ORTHOMCL1958", "ORTHOMCL1984", "ORTHOMCL2001"],
        "35": ["ORTHOMCL421", "ORTHOMCL465", "ORTHOMCL524", "ORTHOMCL525", "ORTHOMCL537", "ORTHOMCL592", "ORTHOMCL652", "ORTHOMCL728", "ORTHOMCL763", "ORTHOMCL780", "ORTHOMCL818", "ORTHOMCL841", "ORTHOMCL858", "ORTHOMCL878", "ORTHOMCL888", "ORTHOMCL1002", "ORTHOMCL1005", "ORTHOMCL1029", "ORTHOMCL1043", "ORTHOMCL1092", "ORTHOMCL1136", "ORTHOMCL1314", "ORTHOMCL1334", "ORTHOMCL1370", "ORTHOMCL1374", "ORTHOMCL1591", "ORTHOMCL1678", "ORTHOMCL1762", "ORTHOMCL1770", "ORTHOMCL1863", "ORTHOMCL1906", "ORTHOMCL1915", "ORTHOMCL1958", "ORTHOMCL1965", "ORTHOMCL1984"],
        "40": ["ORTHOMCL441", "ORTHOMCL525", "ORTHOMCL540", "ORTHOMCL609", "ORTHOMCL613", "ORTHOMCL626", "ORTHOMCL648", "ORTHOMCL650", "ORTHOMCL744", "ORTHOMCL836", "ORTHOMCL838", "ORTHOMCL872", "ORTHOMCL875", "ORTHOMCL884", "ORTHOMCL916", "ORTHOMCL918", "ORTHOMCL938", "ORTHOMCL948", "ORTHOMCL968", "ORTHOMCL989", "ORTHOMCL993", "ORTHOMCL1007", "ORTHOMCL1083", "ORTHOMCL1146", "ORTHOMCL1147", "ORTHOMCL1305", "ORTHOMCL1314", "ORTHOMCL1404", "ORTHOMCL1442", "ORTHOMCL1480", "ORTHOMCL1490", "ORTHOMCL1491", "ORTHOMCL1770", "ORTHOMCL1772", "ORTHOMCL1882", "ORTHOMCL1906", "ORTHOMCL1909", "ORTHOMCL1952", "ORTHOMCL1958", "ORTHOMCL2033"],
        "45": ["ORTHOMCL358", "ORTHOMCL458", "ORTHOMCL525", "ORTHOMCL526", "ORTHOMCL592", "ORTHOMCL625", "ORTHOMCL626", "ORTHOMCL641", "ORTHOMCL667", "ORTHOMCL726", "ORTHOMCL758", "ORTHOMCL790", "ORTHOMCL877", "ORTHOMCL884", "ORTHOMCL974", "ORTHOMCL983", "ORTHOMCL989", "ORTHOMCL1005", "ORTHOMCL1007", "ORTHOMCL1008", "ORTHOMCL1021", "ORTHOMCL1027", "ORTHOMCL1038", "ORTHOMCL1043", "ORTHOMCL1092", "ORTHOMCL1113", "ORTHOMCL1129", "ORTHOMCL1135", "ORTHOMCL1147", "ORTHOMCL1305", "ORTHOMCL1410", "ORTHOMCL1591", "ORTHOMCL1772", "ORTHOMCL1788", "ORTHOMCL1816", "ORTHOMCL1833", "ORTHOMCL1875", "ORTHOMCL1940", "ORTHOMCL1958", "ORTHOMCL1973", "ORTHOMCL1985", "ORTHOMCL1996", "ORTHOMCL1997", "ORTHOMCL2001", "ORTHOMCL2020"],
        "50": ["ORTHOMCL1", "ORTHOMCL256", "ORTHOMCL320", "ORTHOMCL358", "ORTHOMCL458", "ORTHOMCL534", "ORTHOMCL537", "ORTHOMCL592", "ORTHOMCL641", "ORTHOMCL650", "ORTHOMCL667", "ORTHOMCL680", "ORTHOMCL768", "ORTHOMCL818", "ORTHOMCL838", "ORTHOMCL841", "ORTHOMCL853", "ORTHOMCL877", "ORTHOMCL878", "ORTHOMCL888", "ORTHOMCL908", "ORTHOMCL938", "ORTHOMCL974", "ORTHOMCL989", "ORTHOMCL1003", "ORTHOMCL1005", "ORTHOMCL1008", "ORTHOMCL1009", "ORTHOMCL1027", "ORTHOMCL1034", "ORTHOMCL1042", "ORTHOMCL1083", "ORTHOMCL1092", "ORTHOMCL1104", "ORTHOMCL1125", "ORTHOMCL1129", "ORTHOMCL1166", "ORTHOMCL1316", "ORTHOMCL1374", "ORTHOMCL1591", "ORTHOMCL1788", "ORTHOMCL1809", "ORTHOMCL1816", "ORTHOMCL1861", "ORTHOMCL1890", "ORTHOMCL1895", "ORTHOMCL1909", "ORTHOMCL1916", "ORTHOMCL1984", "ORTHOMCL1985"]
    }
    #################################################################

    # for N_FILES in FILE_COUNT_LIST:
    # INPUT_FILE_LIST = dfu.list_first_n_files(input_dir, N_FILES)
        
    for N_FILES, INPUT_FILE_LIST in INPUT_FILE_DICT.items():

        print(f"Using {N_FILES} files: {INPUT_FILE_LIST}")

        for MEMORY in MEMORY_LIST:

            du.override_params(
                workflow_steps, PROVIDER, MEMORY, INPUT_FILE_LIST, SET_ACTIVE_STEPS
            )

            ##
            ## Execute the workflow
            ##
            (
                execution_tag,
                workflow_start_time_ms,
                workflow_end_time_ms,
                runtime_data,
            ) = dexec.execute_workflow(
                workflow_steps,
                env_properties,
            )

            metadata_file = (
                env_properties.get("denethor")
                .get("log.metadata_file")
                .replace("[execution_tag]", execution_tag)
                .replace("[n_files]", f"{int(N_FILES):03}")
                .replace("[memory]", f"{MEMORY:04}")
            )

            log_path = (
                env_properties.get("denethor")
                .get("log.path")
                .replace("[provider_tag]", PROVIDER)
            )

            # Write execution details to log_metadata in JSON format
            metadata_content = {
                "date_time_utc": du.now_str(),
                "workflow_name": workflow_info.get("workflow_name"),
                "execution_tag": execution_tag,
                "workflow_start_time_ms": workflow_start_time_ms,
                "workflow_end_time_ms": workflow_end_time_ms,
                "runtime_data": runtime_data,
                "workflow_steps": workflow_steps,
                "env_properties": env_properties,
            }

            with open(os.path.join(log_path, metadata_file), "w") as mf:
                json.dump(metadata_content, mf, indent=4)

            ##
            ## Import provenance data
            ##
            # dprov.import_provenance_from_aws(
            #         execution_tag,
            #         workflow_start_time_ms,
            #         workflow_end_time_ms,
            #         runtime_data,
            #         provider_info,
            #         workflow_info,
            #         workflow_steps,
            #         statistics_info,
            #         env_properties,
            #     )


if __name__ == "__main__":
    main()
