from denethor.utils import utils as du, file_utils as dfu
import os
import json


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
    return workflow_input_files


# Function to override parameters in the workflow steps dictionary
def override_params(
    workflow_steps: dict,
    provider: str = None,
    memory: str = None,
    input_file_list: list = None,
    active_steps: list = None,
):
    for step in workflow_steps:
        if provider:
            step["provider"] = provider
            print(f"Warning: Overriding environment to {provider}!")
        if memory:
            step["memory"] = memory
            print(
                f"Warning: Overriding memory size of step {step['activity']} to {memory}MB!"
            )
        if input_file_list:
            if step.get("data_params") and step.get("data_params").get(
                "input_files_list"
            ):
                step["data_params"]["input_files_list"] = input_file_list
                print(
                    f"Warning: Overriding input files list of step {step['activity']} to {input_file_list}!"
                )
        if active_steps:
            if step["activity"] in active_steps:
                step["active"] = True
                print(f"Warning: Overriding step {step['activity']} to active!)")
            else:
                step["active"] = False
                print(f"Warning: Overriding step {step['activity']} to inactive!)")


def append_execution_metadata(
    file_path,
    execution_tag,
    n_files,
    memory,
    workflow_start_time_ms,
    workflow_end_time_ms,
    workflow_runtime_data,
    workflow_steps,
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
    Append overall run metadata to the aggregated JSON file.
    """
    with open(file_path, "r+") as f:
        data = json.load(f)

        data["run_metadata"] = {
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
            "provider_info": provider_info,
            "workflow_info": workflow_info,
            "statistics_info": statistics_info,
            "env_properties": env_properties,
        }

        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
