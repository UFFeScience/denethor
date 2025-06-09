import os, sys, timeit, json
from pathlib import Path
from denethor.utils import utils as du, file_utils as dfu
from denethor.executor import execution_manager as dem
from denethor.provenance import provenance_importer as dprov
from denethor import constants as const


def main():
    
    import_start_time = timeit.default_timer()
    import_start_datetime = du.now_str()
    print(">>> Main program started at: ", import_start_datetime)
    
    #################################################################
    #
    # Configure execution parameters
    #
    #################################################################
    
    METADATA_DIR = "resources/logs/aws_ec2"  # or "resources/logs/aws_lambda"
    
    # Recebe o nome do arquivo como parâmetro, ou usa valor padrão
    if len(sys.argv) > 1:
        INPUT_METADATA_FILE = sys.argv[1]
    else:
        INPUT_METADATA_FILE = "run_metadata_2025-06-09T04_05_36UTC.json"

    #################################################################

    
    with open(os.path.join(METADATA_DIR, INPUT_METADATA_FILE), "r") as f:
        run_metadata = json.load(f)
        provider_info = run_metadata["provider_info"]
        workflow_info = run_metadata["workflow_info"]
        statistics_info = run_metadata["statistics_info"]
        env_properties = run_metadata["env_properties"]
        executions = run_metadata["executions"]

    for execution_tag, execution in executions.items():
        
        workflow_start_time_ms = execution["workflow_start_time_ms"]
        workflow_end_time_ms = execution["workflow_end_time_ms"]
        workflow_runtime_data = execution["workflow_runtime_data"]
        workflow_steps = execution["workflow_steps"]

        print(f"\nImporting {execution_tag}")

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

    import_end_time = timeit.default_timer()
    import_duration = import_end_time - import_start_time
    import_end_datetime = du.now_str()

    print("\n\n>>> Main program finished at: ", import_end_datetime)
    print(
        f">>> Total execution time: {int(import_duration // 60)} minutes and {int(import_duration % 60)} seconds"
    )

if __name__ == "__main__":
    main()
