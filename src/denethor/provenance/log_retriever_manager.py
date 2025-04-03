import os, json, time, boto3, datetime
from typing import Dict
from denethor.core.model.Provider import Provider
from denethor.core.model.WorkflowExecution import WorkflowExecution
from denethor.provenance import log_retriever_lambda as lrl, log_retriever_ec2 as lre
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
    Retrieves logs from Provider and saves them to a file.

    Args:
        provider (Provider): The provider object.
        workflow_execution (WorkflowExecution): The workflow execution object.
        activity_name (str): The name of the activity to retrieve logs from.
        env_properties (Dict[str, str]): The environment properties.

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
    
    log_file_name = log_file_name.replace("[activity_name]", activity_name)

    log_file = os.path.join(log_path, log_file_name)


    if provider.provider_tag == const.AWS_LAMBDA:
        
        log_file = lrl.retrieve_logs(
            provider, workflow_execution, activity_name, memory, env_properties, log_file
        )
    elif provider.provider_tag == const.AWS_EC2:
        
        log_file = lre.retrieve_logs(
            provider, workflow_execution, activity_name, env_properties, log_file
        )

    return log_file


# Define a function to print logs in an organized manner
def print_logs_to_console(logs: list) -> None:
    print("-" * 80)
    for log_item in logs:
        # Convert Unix timestamp to human-readable date and time
        log_datetime = datetime.fromtimestamp(log_item["timestamp"] / 1000.0).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        print(f"Timestamp: {log_item['timestamp']}")
        print(f"DateTime: {log_datetime}")
        # print(f"IngestionTime: {item['ingestionTime']}")
        # print(f"EventId: {item['eventId']}")
        print(f"Message: {log_item['message']}")
    print("-" * 80)
