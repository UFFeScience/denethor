from typing import List, Dict, Optional
import os, time, json
from pathlib import Path
from denethor.utils import utils as du
from denethor.core.model import *
from denethor.core.repository import *
from denethor.core.service import *
from . import log_retriever_manager as alr
from . import aws_log_analyzer as ala


def import_provenance_from_aws(
    execution_info: dict,
    workflow_info: dict,
    workflow_steps: List[Dict],
    statistics_info: dict,
    env_properties: Dict[str, str],
) -> None:

    execution_tag = execution_info.get("execution_tag")
    start_time_ms = execution_info.get("workflow_start_time_ms")
    end_time_ms = execution_info.get("workflow_end_time_ms")
    runtime_data = execution_info.get("runtime_data")

    prov_start_time_ms = int(time.time() * 1000)
    prov_end_time_ms = None

    print(f"Starting importing provenance from AWS | Execution Tag: {execution_tag}")

    print(
        f"\n>>> Provenance import start time is: {prov_start_time_ms} ms | {du.convert_ms_to_str(prov_start_time_ms)}"
    )

    workflow = workflow_service.get_by_name(workflow_info.get("workflow_name"))
    
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
        provider = provider_service.get_by_tag(provider_tag)

        print(
            f"Importing provenance from AWS:\n Execution Tag: {execution_tag}\n Activity: {activity_name}\n Memory: {memory}\n Activity: {activity_name}\n Start Time: {start_time_ms}\n End Time: {end_time_ms}"
        )

        # Retrieve logs from AWS
        log_file = alr.retrieve_logs(
            provider,
            workflow_execution,
            activity_name,
            memory,
            env_properties,
        )

        # Extract and persist log data into the database
        ala.extract_and_persist_log_data(
            provider,
            workflow_execution,
            activity_name,
            memory,
            log_file,
            statistics_info,
        )

    print(f"Finished importing provenance from AWS | Execution Tag: {execution_tag}")

    prov_end_time_ms = int(time.time() * 1000)

    print(
        f">>> Provenance import start time: {du.convert_ms_to_str(prov_start_time_ms)}"
    )

    print(f">>> Provenance import end time: {du.convert_ms_to_str(prov_end_time_ms)}")

    print(f">>> Provenance import duration: {prov_end_time_ms - prov_start_time_ms} ms")
