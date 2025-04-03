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
    env_properties: Dict[str, str],
    log_file: str,
) -> str:
    """
    Retrieves logs from AWS EC2 and saves them to a file.

    Raises:
        ValueError: If no log records were found.

    Returns:
        str: The name of the log file with path.
    """


    # retrieve logs from EC2 instance
    # call retrieve_logs_from_ec2_instance.sh with wetag parameter
    
    
    return log_file
