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
    FORCE_PROVIDER = const.AWS_EC2
    FORCE_MEMORY = 1024

    INPUT_FILE_LIST = None

    file_count = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    # file_count = 50

    INPUT_FILE_LIST = dfu.list_first_n_files(input_dir, file_count)

    print(f"Using {file_count} files: {INPUT_FILE_LIST}")
    du.override_params(workflow_steps, FORCE_PROVIDER, FORCE_MEMORY, INPUT_FILE_LIST)

    #################################################################

    ##
    ## Execute the workflow
    ##
    execution_tag, workflow_start_time_ms, workflow_end_time_ms, runtime_data = (
        dexec.execute_workflow(
            workflow_steps,
            env_properties,
        )
    )

    metadata_file = (
        env_properties.get("denethor")
        .get("log.metadata_file")
        .replace("[execution_tag]", execution_tag)
    )

    log_path = (
        env_properties.get("denethor")
        .get("log.path")
        .replace("[provider_tag]", FORCE_PROVIDER)
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
