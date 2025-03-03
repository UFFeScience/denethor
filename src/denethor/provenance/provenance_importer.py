from typing import List, Dict, Optional
import os, time, json
from pathlib import Path
from denethor.utils import utils as du
from denethor.core.model import *
from denethor.core.repository import *
from denethor.core.service import *
from . import aws_log_retriever as alr
from . import aws_log_analyzer as ala


def import_provenance_from_aws(
    execution_tag: str,
    workflow_steps: List[Dict],
    start_time_ms: int,
    end_time_ms: int,
    provider: Provider,
    workflow: Workflow,
    runtime_data: dict,
    statistics_info: dict,
    env_properties: Dict[str, str],
) -> None:

    prov_start_time_ms = int(time.time() * 1000)
    prov_end_time_ms = None

    print(
        f"\n>>> Provenance import start time is: {prov_start_time_ms} ms | {du.convert_ms_to_str(prov_start_time_ms)}"
    )

    workflow_execution = workflow_execution_service.create(
        workflow,
        execution_tag,
        start_time_ms,
        end_time_ms,
        runtime_data,
    )

    # For each step in the workflow
    for step in workflow_steps:

        # Check if the step is active
        if step.get("active") is False:
            print(f"\n>>> Activity: {activity_name} is inactive. Skipping...")
            continue

        activity_name = step.get("activity")
        memory = step.get("memory")
        provider_tag = step.get("provider")

        function_name = activity_name + "_" + str(memory)

        print(
            f"Importing provenance from AWS:\n Execution ID: {execution_tag}\n Activity: {activity_name}\n Memory: {memory}\n Function: {function_name}\n Start Time: {start_time_ms}\n End Time: {end_time_ms}\n Log File: {log_file}"
        )

        # Retrieve logs from AWS
        log_file = alr.retrieve_logs_from_aws(
            provider_tag,
            execution_tag,
            function_name,
            start_time_ms,
            end_time_ms,
            env_properties,
        )

        # Extract and persist log data into the database
        ala.extract_and_persist_log_data(
            execution_tag,
            activity_name,
            memory,
            log_file,
            provider,
            workflow,
            workflow_execution,
            statistics_info,
        )

    print("Finished importing provenance from AWS")

    prov_end_time_ms = int(time.time() * 1000)

    print(
        f">>> Provenance import start time: {du.convert_ms_to_str(prov_start_time_ms)}"
    )

    print(f">>> Provenance import end time: {du.convert_ms_to_str(prov_end_time_ms)}")

    print(f">>> Provenance import duration: {prov_end_time_ms - prov_start_time_ms} ms")
