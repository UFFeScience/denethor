import json, os, re

from denethor.core.model import *
from denethor.core.service import *
from denethor.core.repository import *
from . import log_parser as parser
from denethor.utils import utils as du, log_utils as dlu
from denethor import constants as const


def extract_and_persist_log_data(
    provider: Provider,
    workflow_execution: WorkflowExecution,
    activity_name: str,
    memory: int,
    log_file: str,
    statistics_dict: dict,
) -> None:
    """
    Extracts and persists the log data from the log file to the database.

    Args:
        - provider: The provider object persisted in the database.
        - workflow_execution: The workflow execution object persisted in the database.
        - activity_name (str): The activity name (e.g., 'tree_constructor').
        - memory (int): The memory size of the Lambda function.
        - log_file (str): The name of the log file.
        - statistics_dict (dict): Information about the statistics.

    Raises:
        ValueError: If the activity is not found in the workflow activities JSON file.

    Returns:
        None
    """

    # Retrieving the provider, workflow, activity and configuration from the database and checking if they exist
    activity = workflow_activity_service.get_by_name_and_workflow(
        activity_name, workflow_execution.workflow
    )

    provider_conf = provider_conf_service.get_by_provider_and_memory(provider, memory)

    with open(log_file) as f:
        log_data = json.load(f)

    # Filters and organizes log records by RequestId
    logs_by_request = dlu.group_logs_by_request(log_data)

    # Iterating over the set of logs for a request_id
    # Each set represents a complete execution of the activity for a set of input files (i.e., a task)
    for request_id, logs in logs_by_request.items():

        print(
            f"\n------------------------------------------------------------------------------------"
        )
        print(f"Parsing Logs of {activity_name} | RequestId: {request_id}")
        print(
            f"------------------------------------------------------------------------------------"
        )

        service_execution = ServiceExecution(
            request_id=request_id,
            log_stream_name=logs[0]["logStreamName"],
            workflow_execution=workflow_execution,
            activity=activity,
            provider_conf=provider_conf,
        )

        parser.parse_execution_logs(service_execution, logs, statistics_dict)

        if service_execution.memory_size and memory != service_execution.memory_size:
            raise ValueError(
                f"Memory size in log mismatch for {activity_name} | RequestId: {request_id} | Expected: {memory} | Found: {service_execution.memory_size}"
            )

        print(
            f">>>> Saving Execution info of {activity_name} | RequestId: {request_id} to Database"
        )

        # verificar se os registros presentes no Log já estão cadastrados na base
        # caso positivo -> apenas recupera o registro
        # caso negativo -> realiza a inclusão e retorna o novo registro
        service_execution_db, se_created = service_execution_repo.get_or_create(
            service_execution
        )
        print(
            f'{">>>>>> Saving" if se_created else "Retrieving"} Service Execution info: [{service_execution_db.se_id}]={activity.activity_name} ({service_execution_db.duration} ms)'
        )

        # Process execution files in batch
        execution_file_service.process_execution_files_in_batch(
            service_execution.execution_files, service_execution_db
        )

        # para a execução da função verificamos se existem estatísticas adicionais para armazenar
        for exec_stat in service_execution.execution_statistics:
            # nesse ponto assumimos que a estatística já foi incluída no banco de dados
            statistics_db = statistics_repo.get_by_name(
                exec_stat.statistics.statistics_name
            )
            if not statistics_db:
                raise ValueError(
                    f"Statistics {exec_stat.statistics.name} not found in Database!"
                )
            exec_stat.statistics = statistics_db
            exec_stat.service_execution = service_execution_db
            exec_stat_db, es_created = execution_statistics_repo.get_or_create(
                exec_stat
            )
            print(
                f'>>Retrieving Statistics: {statistics_db} | {"Saving" if es_created else "Retrieving"} Execution Statistics info: {exec_stat_db}'
            )

        print(
            f"Finished saving Service Execution info to Database: {service_execution_db}"
        )
