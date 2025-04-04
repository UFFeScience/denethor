import os, json, time, boto3, datetime
from typing import Dict
from denethor.core.model.Provider import Provider
from denethor.core.model.WorkflowExecution import WorkflowExecution
from denethor.utils import utils as du
from denethor import constants as const


def retrieve_logs(
    provider: Provider,
    workflow_execution: WorkflowExecution,
    activity_name: str,
    memory: int,
    env_properties: Dict[str, str],
) -> str:
    """
    Retrieves logs from AWS LAMBDA and saves them to a file.

    Raises:
        ValueError: If no log records were found.

    Returns:
        str: The name of the log file with path.
    """

    log_path = env_properties.get("denethor").get("log.path")
    log_file_name = env_properties.get("denethor").get("log.file")

    log_path = log_path.replace("[provider_tag]", provider.provider_tag)
    log_file_name = log_file_name.replace(
        "[execution_tag]", workflow_execution.execution_tag
    )
    
    function_name = activity_name + f"_{memory}"
    log_file_name = log_file_name.replace("[activity_name]", function_name)
    log_file = os.path.join(log_path, log_file_name)

    log_group_name = f"/aws/lambda/{function_name}"

    start_time_ms = workflow_execution.get_start_time_ms()
    end_time_ms = workflow_execution.get_end_time_ms()

    logs = get_all_log_events(log_group_name, start_time_ms, end_time_ms)

    if logs == None or len(logs) == 0:
        raise ValueError(
            f"No log records were found! log_group_name={log_group_name}, start_time={start_time_ms}, end_time={end_time_ms}"
        )

    save_log_file(logs, log_file)

    print(
        f"Logs for function {function_name}, execution {workflow_execution} saved to {log_file} in JSON format"
    )

    return log_file


def get_all_log_events(
    log_group_name: str, start_time_ms: int, end_time_ms: int, filter_pattern: str = ""
):

    client = boto3.client("logs")

    all_events = []
    next_token = None

    if not end_time_ms:
        end_time_ms = int(time.time() * 1000)

    # Ensure the minimal interval (after end_time) before retrieving logs from aws
    current_time_ms = int(time.time() * 1000)
    elapsed_time_ms = current_time_ms - end_time_ms
    wait_time_before_log_fetch_ms = const.LOG_RETRIEVAL_DELAY_MS - elapsed_time_ms
    if wait_time_before_log_fetch_ms > 0:
        print(
            f"Sleeping for {wait_time_before_log_fetch_ms} ms before importing provenance data..."
        )

        time.sleep(wait_time_before_log_fetch_ms / 1000)

    # If there are more log events than the limit, the response will contain a 'nextToken' field
    # This token can be used to retrieve the next batch of log events
    while True:
        if next_token:
            response = client.filter_log_events(
                logGroupName=log_group_name,
                startTime=int(start_time_ms),
                endTime=int(end_time_ms),
                filterPattern=filter_pattern,
                nextToken=next_token,
            )
        else:
            response = client.filter_log_events(
                logGroupName=log_group_name,
                startTime=int(start_time_ms),
                endTime=int(end_time_ms),
                filterPattern=filter_pattern,
            )

        all_events.extend(response["events"])

        next_token = response.get("nextToken")
        if not next_token:
            break

    return all_events


# Save logs to a single file ordered by logStreamName
def save_log_file(json_logs: list, file_name_with_path: str) -> None:

    # Ensure that logs contain the 'logStreamName' and 'timestamp' fields
    if not all("logStreamName" in log and "timestamp" in log for log in json_logs):
        raise ValueError("Logs must contain 'logStreamName' and 'timestamp' fields")

    json_logs.sort(key=lambda x: (x["logStreamName"], x["timestamp"]))

    # Sanitize file name
    file_name_with_path = du.sanitize(file_name_with_path)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_name_with_path), exist_ok=True)

    with open(file=file_name_with_path, mode="w", encoding="utf-8") as file:
        json.dump(json_logs, file, ensure_ascii=False, indent=4)


