import os, time, json
from pathlib import Path
from denethor import constants as denv
from denethor.core.service import *
from denethor.utils import utils as du, file_utils as dfu
from denethor.provenance import provenance_importer as dprov
from denethor.executor import workflow_executor as dexec
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


def main():

    print(">>> Main program started at: ", du.now_str())

    #################################################################
    #
    # !!!! Force execution parameters !!!!
    #
    #################################################################
    FORCE_ENV = None
    FORCE_MEMORY = [128, 256, 512, 1024, 2048]

    #################################################################

    for memory in FORCE_MEMORY:
        
        override_params(FORCE_ENV, memory)

        ##
        ## Execute the workflow
        ##
        execution_info = dexec.execute_workflow(
            provider_info,
            workflow_info,
            workflow_steps,
            statistics_info,
            env_properties,
        )

        ##
        ## Import provenance data
        ##
        dprov.import_provenance_from_aws(
            execution_info,
            workflow_info,
            workflow_steps,
            statistics_info,
            env_properties,
        )

    print(">>> Main program finished at: ", du.now_str())


def override_params(env=None, memory=None):
    for step in workflow_steps:
        if env:
            step['provider'] = env
            print(f"Warning: Overriding environment to {env}!")
        if memory:
            step['memory'] = memory
            print(f"Warning: Overriding memory size of step {step['activity']} to {memory}MB!")


if __name__ == "__main__":
    main()
