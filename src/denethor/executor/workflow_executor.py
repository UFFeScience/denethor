from typing import List, Dict, Optional
import os, time, json
from pathlib import Path
from denethor.utils import utils as du, file_utils as dfu
from denethor.executor import execution_manager as dem
from denethor.core.model import *
from denethor.core.repository import *
from denethor.core.service import *

# Dictionary to store the produced data during the workflow execution
runtime_data = {}

def execute_workflow(
    provider_info: dict,
    workflow_info: dict,
    workflow_steps: List[Dict],
    statistics_info: dict,
    env_properties: Dict[str, str],
) -> None:

    # Save Workflow Basic Information: Provider, Workflow, Activities, Statistics, Configurations
    provider_service.get_or_create(provider_info)
    workflow_service.get_or_create(workflow_info)
    statistics_service.get_or_create(statistics_info)

    # Set the workflow start time in milliseconds
    workflow_start_time_ms = int(time.time() * 1000)
    workflow_end_time_ms = None

    execution_tag = du.generate_execution_tag(workflow_start_time_ms)

    print(
        f"\n>>> Workflow {execution_tag} start time is: {workflow_start_time_ms} ms | {du.convert_ms_to_str(workflow_start_time_ms)}"
    )
    print(">>> Execution TAG: ", execution_tag)
    print(">>> Working directory: ", os.getcwd())

    previous_activity = None

    # For each step in the workflow
    for step in workflow_steps:

        activity = step.get("activity")
        provider_tag = step.get("provider")
        memory = step.get("memory")
        strategy = step.get("strategy")
        data_params = step.get("data_params")
        param_in = data_params.get("param_in")
        param_out = data_params.get("param_out")

        # Check if the step is active
        if step.get("active") is False:
            print(f"\n>>> Activity: {activity} is inactive. Skipping...")
            continue

        # Validation of input parameter
        if param_in is None:
            raise ValueError(
                f"Invalid input parameter: {param_in} for activity: {activity}"
            )

        # caso input_files_path esteja presente, significa que os dados de entrada serão lidos de um diretório
        input_files_path = data_params.get("input_files_path")
        input_files_list = data_params.get("input_files_list")
        if input_files_path:
            input_files = dfu.list_files(input_files_path, input_files_list)
            runtime_data[param_in] = [{"data": f} for f in input_files]

        # recuperar os dados  em runtime indicados por 'input_param_name'
        # input_data será uma lista dos dados necessários para a atividade corrente
        input_data = []
        for key, data in runtime_data.items():
            if key == param_in:
                input_data = [item["data"] for item in data]
                break


        # Execute the activity
        results = dem.execute_activity(
            execution_tag,
            provider_tag,
            strategy,
            activity,
            previous_activity,
            memory,
            input_data,
            env_properties,
        )

        # Save the produced data in the dictionary
        runtime_data[param_out] = results
        previous_activity = activity

        print(
            f"\n>>> Activity execution of {activity} | Memory: {memory} | Strategy: {strategy} completed."
        )

    workflow_end_time_ms = int(time.time() * 1000)

    print(
        f"\n>>> Workflow {execution_tag} start time is: {workflow_start_time_ms} ms | {du.convert_ms_to_str(workflow_start_time_ms)}"
    )
    print(
        f">>> Workflow {execution_tag} end time is: {workflow_end_time_ms} ms | {du.convert_ms_to_str(workflow_end_time_ms)}"
    )
    print(
        f">>> Workflow {execution_tag} duration: {workflow_end_time_ms - workflow_start_time_ms} ms"
    )

    return {
        "execution_tag": execution_tag,
        "workflow_start_time_ms": workflow_start_time_ms,
        "workflow_end_time_ms": workflow_end_time_ms,
        "runtime_data": runtime_data,
    }
