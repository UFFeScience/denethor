import json, os, re
from . import log_parser as parser
from denethor.database.model import *
from denethor.database.repository import *


def process_and_save_logs(
    execution_id: str,
    activity_name: str,
    memory: int,
    log_file: str,
    providers: dict,
    workflow_dict: dict,
    statistics_dict: dict,
):
    """
    Analyzes logs based on the provided parameters.

    Args:
        - execution_id (str): The execution ID (e.g., 'exec_2024-08-02_00-54-08+00-00_UTC').
        - activity_name (str): The activity name (e.g., 'tree_constructor').
        - memory (int): The memory size of the Lambda function.
        - log_file (str): The name of the log file.
        - providers (list): A list of dictionaries containing information about the service providers.
        - workflow_dict (dict): Information about the workflow, including the activities.
        - statistics_dict (dict): Information about the statistics.

    Raises:
        ValueError: If the activity is not found in the workflow activities JSON file.

    Returns:
        None
    """

    # Retrieving the provider, workflow, activity and configuration from the database and checking if they exist
    workflow_db = get_workflow(workflow_dict)
    provider_db = get_provider(workflow_dict, activity_name)
    activity_db = get_activity(activity_name, workflow_db)
    configuration_db = get_provider_configuration(provider_db, memory)

    with open(log_file) as f:
        log_data = json.load(f)

    # Filters and organizes log records by RequestId
    logs_by_request = group_logs_by_request(log_data)

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

        service_execution = parser.parse_execution_logs(
            request_id, logs, statistics_dict
        )

        service_execution.workflow_execution_id = execution_id
        service_execution.activity = activity_db
        service_execution.provider = provider_db
        service_execution.provider_configuration = configuration_db

        if memory != service_execution.memory_size:
            raise ValueError(
                f"Memory size in log mismatch for {activity_name} | RequestId: {request_id} | Expected: {memory} | Found: {service_execution.memory_size}"
            )

        # print(service_execution)

        print(
            f"\n--------------------------------------------------------------------------"
        )
        print(
            f"Saving Execution info of {activity_name} | RequestId: {request_id} to Database"
        )
        print(
            f"--------------------------------------------------------------------------"
        )

        # verificar se os registros presentes no Log já estão cadastrados na base
        # caso positivo -> apenas recupera o registro
        # caso negativo -> realiza a inclusão e retorna o novo registro
        service_execution_db, se_created = service_execution_repo.get_or_create(
            service_execution
        )
        print(
            f'{">>Saving" if se_created else "Retrieving"} Service Execution info: [{service_execution_db.se_id}]={activity_db.activity_name} ({service_execution_db.duration} ms)'
        )

        # para cada arquivo de entrada e registro de execução do arquivo,
        # verificamos se ambos já estão cadastrados na base
        for exec_file in service_execution.execution_files:
            file_db, file_created = file_repo.get_or_create(exec_file.file)

            exec_file.service_execution = service_execution_db
            exec_file.file = file_db
            exec_file_db, ef_created = execution_file_repo.get_or_create(exec_file)
            print(
                f'{">>Saving" if file_created else "Retrieving"} File: {file_db} | {"Saving" if ef_created else "Retrieving"} Execution_File: {exec_file_db}'
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


## Filters and organizes log records by RequestId
# Each set represents a complete execution of the activity for a set of input files
def group_logs_by_request(logs: dict) -> dict:

    # Dicionário para armazenar os logs filtrados
    logs_by_request = {}

    # Loop através dos logs
    for log in logs:
        # Obter o RequestId do log
        request_id = get_request_id(log["message"])

        # Se o RequestId não for None, adicione o log ao dicionário
        if request_id is not None:
            if request_id not in logs_by_request:
                logs_by_request[request_id] = []
            logs_by_request[request_id].append(log)

    return logs_by_request


def get_request_id(log_message):
    match = re.search("RequestId: (\\S+)", log_message)
    request_id = match.group(1) if match else None
    return request_id


def get_workflow(workflow_dict: dict) -> Workflow:
    workflow_name = workflow_dict["workflow_name"]
    workflow_db = workflow_repo.get_by_name(workflow_name)
    if not workflow_db:
        raise ValueError(f"Workflow {workflow_name} not found in Database!")
    return workflow_db


def get_activity(activity_name: str, workflow_db: Workflow) -> WorkflowActivity:
    activity_db = workflow_activity_repo.get_by_name_and_workflow(
        activity_name, workflow_db
    )
    if not activity_db:
        raise ValueError(f"Activity {activity_name} not found in Database!")
    return activity_db


def get_provider(workflow_dict: dict, activity_name: str) -> Provider:

    # Finding the corresponding activity in the workflow activities JSON file
    activities_dict = workflow_dict["activities"]
    activity = next(
        (act for act in activities_dict if act["activity_name"] == activity_name),
        None,
    )
    if not activity:
        raise ValueError(
            f"Activity {activity_name} not found in the workflow activities JSON file"
        )

    provider_name = activity["provider_name"]
    if not provider_name:
        raise ValueError(f"Provider name not found for Activity {activity_name}")

    provider_db = provider_repo.get_by_name(provider_name)

    if not provider_db:
        raise ValueError(f"Provider {provider_name} not found in Database!")
    return provider_db


def get_provider_configuration(provider: Provider, memory: int) -> ProviderConfiguration:
    provider_configuration_db = provider_configuration_repo.get_by_provider_and_memory(
        provider, memory
    )
    if not provider_configuration_db:
        raise ValueError(
            f"Provider Configuration for memory {memory} not found in Database!"
        )
    return provider_configuration_db
