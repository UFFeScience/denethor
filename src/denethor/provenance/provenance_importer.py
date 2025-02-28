from denethor.database.model import *
from denethor.database.repository import *
from denethor.core.service import *
from . import aws_log_retriever as alr
from . import aws_log_analyzer as ala
import denethor.utils.utils as du

def import_provenance_from_aws(
    execution_tag: str,
    activity_name: str,
    memory: int,
    start_time_ms: int,
    end_time_ms: int,
    log_file_with_path: str,
    workflow_info: dict,
    statistics_info: dict,
) -> None:

    function_name = activity_name
    if memory:
        function_name += "_" + str(memory)

    print(
        f"Importing provenance from AWS:\n Execution ID: {execution_tag}\n Activity Name: {activity_name}\n Memory: {memory}\n Function Name: {function_name}\n Start Time: {start_time_ms}\n End Time: {end_time_ms}\n Log File: {log_file_with_path}"
    )

    alr.retrieve_logs_from_aws(
        execution_tag, function_name, start_time_ms, end_time_ms, log_file_with_path
    )

    ala.process_and_save_logs(
        execution_tag,
        activity_name,
        memory,
        log_file_with_path,
        workflow_info,
        statistics_info,
    )

    print("Finished importing provenance from AWS")

