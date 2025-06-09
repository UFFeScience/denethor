from denethor.utils import utils as du, file_utils as dfu
import os
import json


def setup_metadata_json_file(run_start_datetime, env_properties, provider_tag):
    log_path = (
        env_properties.get("denethor")
        .get("log.path")
        .replace("[provider_tag]", provider_tag)
    )

    # Generate a unique suffix for the metadata file
    sufix = du.sanitize(run_start_datetime.replace("+00:00", "UTC"))

    run_metadata_file = os.path.join(log_path, f"run_metadata_{sufix}.json")

    # Initialize the JSON file with an empty dictionary if it doesn't exist
    if not os.path.exists(run_metadata_file):
        with open(run_metadata_file, "w") as f:
            json.dump({}, f, indent=4)
    return run_metadata_file


def select_input_files_for_workflow(
    file_count_list, file_selection_mode, input_dir
) -> dict:
    """
    Build a dictionary of input files for the workflow based on the specified file count and selection mode.
    Args:
        file_count_list (list): List of file counts to select from.
        file_selection_mode (str): Mode of file selection ("random" or "first").
        input_dir (str): Directory containing the input files.
    Returns:
        dict: Dictionary with file counts as keys and lists of selected files as values.
    """
    workflow_input_files = {}
    for n_files in file_count_list:
        if file_selection_mode == "random":
            # randomly select N_FILES from input_dir
            workflow_input_files[n_files] = dfu.list_random_n_files(input_dir, n_files)
        elif file_selection_mode == "first":
            # select first N_FILES from input_dir
            workflow_input_files[n_files] = dfu.list_first_n_files(input_dir, n_files)
        else:
            raise ValueError(
                f"Invalid file selection mode: {file_selection_mode}. "
                "Use 'random' or 'first'."
            )
    return workflow_input_files


# Function to update workflow step parameters based on provided configurations
def update_workflow_step_parameters(
    workflow_steps: dict,
    provider: str = None,
    memory: str = None,
    input_file_list: list = None,
    active_steps: list = None,
):
    for step in workflow_steps:
        if provider:
            step["provider"] = provider
            print(f"Updating provider of step {step['activity']} to {provider}!")

        if memory:
            step["memory"] = memory
            print(f"Updating memory of step {step['activity']} to {memory} MB!")

        if input_file_list:
            if step.get("data_params") and step.get("data_params").get(
                "input_files_list"
            ):
                step["data_params"]["input_files_list"] = input_file_list
                print(
                    f"Updating input files of step {step['activity']} to {input_file_list}!"
                )
        
        if active_steps:
            if step["activity"] in active_steps:
                step["active"] = True
                print(f"Updating step {step['activity']} to active!)")
            else:
                step["active"] = False
                print(f"Updating step {step['activity']} to inactive!)")


def append_execution_metadata(
    file_path,
    execution_tag,
    n_files,
    memory,
    workflow_start_time_ms,
    workflow_end_time_ms,
    workflow_runtime_data,
    workflow_steps,
    errors=[],
):
    """
    Append execution metadata to the aggregated JSON file.
    """
    with open(file_path, "r+") as f:
        data = json.load(f)
        if "executions" not in data:
            data["executions"] = {}

        data["executions"][execution_tag] = {
            "n_files": n_files,
            "memory": memory,
            "workflow_start_time_ms": workflow_start_time_ms,
            "workflow_end_time_ms": workflow_end_time_ms,
            "workflow_runtime_data": workflow_runtime_data,
            "workflow_steps": workflow_steps,
            "errors": errors,
        }

        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


def append_run_metadata(
    file_path,
    run_start_datetime,
    run_end_datetime,
    run_duration,
    workflow_name,
    provider,
    memory_list,
    set_active_steps,
    file_selection_mode,
    file_count_list,
    workflow_input_files_by_count,
    provider_info,
    workflow_info,
    statistics_info,
    env_properties,
):
    """
    Append overall run metadata to the aggregated JSON file,
    ensuring 'run_metadata' is the first key in the file.
    Assumes only 'executions' exists before writing.
    """
    with open(file_path, "r+") as f:
        current_json = json.load(f)

        run_details = {
            "run_start_time": run_start_datetime,
            "run_end_time": run_end_datetime,
            "run_duration": run_duration,
            "workflow_name": workflow_name,
            "provider": provider,
            "memory_list": memory_list,
            "set_active_steps": set_active_steps,
            "file_selection_mode": file_selection_mode,
            "file_count_list": file_count_list,
            "workflow_input_files_by_count": workflow_input_files_by_count,
        }

        executions = current_json.get("executions", {})

        # Write run_details and each info tag at the top level
        full_json = {
            "run_details": run_details,
            "provider_info": provider_info,
            "workflow_info": workflow_info,
            "statistics_info": statistics_info,
            "env_properties": env_properties,
            "executions": executions
        }

        f.seek(0)
        json.dump(full_json, f, indent=4)
        f.truncate()
