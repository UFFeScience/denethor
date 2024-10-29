from . import log_parser  as parser
from denethor.database.models.Provider import Provider
from denethor.database.models.ProviderConfiguration import ProviderConfiguration
from denethor.database.models.Workflow import Workflow
from denethor.database.models.WorkflowActivity import WorkflowActivity
from denethor.database.models.File import File
from denethor.database.models.ExecutionFile import ExecutionFile
from denethor.database.models.Statistics import Statistics
from denethor.database.models.ExecutionStatistics import ExecutionStatistics
from denethor.database.models.ServiceExecution import ServiceExecution

from denethor.database.repository.ProviderRepository import ProviderRepository
from denethor.database.repository.ProviderConfigurationRepository import ProviderConfigurationRepository
from denethor.database.repository.WorkflowRepository import WorkflowRepository
from denethor.database.repository.WorkflowActivityRepository import WorkflowActivityRepository
from denethor.database.repository.FileRepository import FileRepository
from denethor.database.repository.ExecutionFileRepository import ExecutionFileRepository
from denethor.database.repository.StatisticsRepository import StatisticsRepository
from denethor.database.repository.ExecutionStatisticsRepository import ExecutionStatisticsRepository
from denethor.database.repository.ServiceExecutionRepository import ServiceExecutionRepository

import json, os, re

from denethor.database import conn

# Instânciando a sessão do banco de dados
session = conn.Connection().get_session()

# Instânciando as classes de repositórios
provider_repo = ProviderRepository(session)
provider_configuration_repo = ProviderConfigurationRepository(session)
workflow_repo = WorkflowRepository(session)
workflow_activity_repo = WorkflowActivityRepository(session)
file_repo = FileRepository(session)
execution_file_repo = ExecutionFileRepository(session)
statistics_repo = StatisticsRepository(session)
execution_statistics_repo = ExecutionStatisticsRepository(session)
service_execution_repo = ServiceExecutionRepository(session)

def process_and_save_logs(params):
    """
    Analyzes logs based on the provided parameters.

    Args:
        params (dict): A dictionary containing the parameters for log analysis.
            - execution_id (str): The execution ID (e.g., 'exec_2024-08-02_00-54-08+00-00_UTC').
            - start_time_ms (float): The start time in milliseconds (e.g., 1722560048000.0).
            - end_time_ms (float): The end time in milliseconds (e.g., 1722565559000.0).
            - activity (str): The activity name (e.g., 'tree_constructor').
            - log_path (str): The path to save the log files.
            - log_file (str): The name of the log file.
            - providers (list): A list of dictionaries containing information about the service providers.
            - workflow (dict): Information about the workflow, including the activities.
            - statistics (dict): Information about the statistics.

    Raises:
        ValueError: If the activity is not found in the workflow activities JSON file.
    
    Returns:
        None
    """
    # Workflow runtime parameters
    execution_id = params['execution_id']

    # Step params
    activities = params['activity']
    # IF functions is not a list, convert it to a list
    if not isinstance(activities, list):
        activities = [activities]

    log_path = params.get('log_path')
    log_file = params.get('log_file')

    workflow_dict = params['workflow']
    activities_dict = workflow_dict['activities']
    statistics = params['statistics']

    # Workflow Activity
    for activity_name in activities:

        # Finding the corresponding activity in the workflow activities JSON file
        activity = next((act for act in activities_dict if act['activity_name'] == activity_name), None)
        if not activity:
            raise ValueError(f"Activity {activity_name} not found in the workflow activities JSON file")
        
        # Retrieving the provider, workflow, and activity from the database and checking if they exist
        workflow_db = workflow_repo.get_by_name(workflow_dict['workflow_name'])
        if not workflow_db:
            raise ValueError(f"Workflow {workflow_dict['workflow_name']} not found in Database!")
        
        activity_db = workflow_activity_repo.get_by_name_and_workflow(activity_name, workflow_db)
        if not activity_db:
            raise ValueError(f"Activity {activity_name} not found in Database!")
        
        provider_db = provider_repo.get_by_name(activity['provider_name'])
        if not provider_db:
            raise ValueError(f"Provider {activity['provider_name']} not found in Database!")
        
        configurations_db = provider_configuration_repo.get_by_provider_id(provider_db.provider_id)
        if not configurations_db:
            raise ValueError(f"Provider Configuration for {provider_db} not found in Database!")
        


        # Opening the log file for the activity, in json format
        log_file_name = log_file.replace('[activity_name]', activity_name).replace('[execution_id]', execution_id)
        file = os.path.join(log_path, log_file_name)
        with open(file) as f:
            log_data = json.load(f)

        # Filters and organizes log records by RequestId
        # Each set represents a complete execution of the activity for a set of input files
        logs_by_request = group_logs_by_request(log_data)

        # Iterating over the set of logs for a request_id (an execution of the lambda function)
        for request_id, logs in logs_by_request.items():
            
            print(f"--------------------------------------------------------------------------")
            print(f'Parsing Logs of {activity_name} | RequestId: {request_id}')
            print(f"--------------------------------------------------------------------------")

            service_execution = parser.parse_execution_logs(request_id, activity_name, logs, statistics)
            
            service_execution.provider = provider_db
            service_execution.activity = activity_db
            service_execution.workflow_execution_id = execution_id

            # find the proper configuration by the memory size recovered from the log
            memory = service_execution.memory_size
            for config in configurations_db:
                if config.memory_mb == memory:
                    service_execution.provider_configuration = config
                    break
            
            # print(service_execution)

            
            print(f"--------------------------------------------------------------------------")
            print(f'Saving Execution info of {activity_name} | RequestId: {request_id} to Database...')
            print(f"--------------------------------------------------------------------------")


            # verificar se os registros presentes no Log já estão cadastrados na base
            # caso positivo -> apenas recupera o registro
            # caso negativo -> realiza a inclusão e retorna o novo registro
            service_execution_db, se_created = service_execution_repo.get_or_create(service_execution)
            print(f'{"Saving" if se_created else "Retrieving"} Service Execution info: [{service_execution_db.se_id}]={activity_db.activity_name} ({service_execution_db.duration} ms)')

            # para cada arquivo de entrada e registro de execução do arquivo,
            # verificamos se ambos já estão cadastrados na base
            for exec_file in service_execution.execution_files:
                file_db, file_created = file_repo.get_or_create(exec_file.file)
                
                exec_file.service_execution = service_execution_db
                exec_file.file = file_db
                exec_file_db, ef_created = execution_file_repo.get_or_create(exec_file)
                print(f'{"Saving" if file_created else "Retrieving"} File: {file_db} | {"Saving" if ef_created else "Retrieving"} Execution_File: {exec_file_db}')

            # para a execução da função verificamos se existem estatísticas adicionais para armazenar
            for  exec_stat in service_execution.execution_statistics:
                # nesse ponto assumimos que a estatística já foi incluída no banco de dados
                statistics_db = statistics_repo.get_by_name(exec_stat.statistics.statistics_name)
                if not statistics_db:
                    raise ValueError(f"Statistics {exec_stat.statistics.name} not found in Database!")
                exec_stat.statistics = statistics_db
                exec_stat.service_execution = service_execution_db
                exec_stat_db, es_created = execution_statistics_repo.get_or_create(exec_stat)
                print(f'Retrieving Statistics: {statistics_db} | {"Saving" if es_created else "Retrieving"} Execution Statistics info: {exec_stat_db}')
                
                
            print(f'Finished saving Service Execution info to Database: {service_execution_db}')
            print(f'\n\n')



## Filters and organizes log records by RequestId
# Each set represents a complete execution of the activity for a set of input files 
def group_logs_by_request(logs: dict) -> dict:
    
    # Dicionário para armazenar os logs filtrados
    logs_by_request = {}
   
    # Loop através dos logs
    for log in logs:
        # Obter o RequestId do log
        request_id = get_request_id(log['message'])
        
        # Se o RequestId não for None, adicione o log ao dicionário
        if request_id is not None:
            if request_id not in logs_by_request:
                logs_by_request[request_id] = []
            logs_by_request[request_id].append(log)

    return logs_by_request


def get_request_id(log_message):
    match = re.search('RequestId: (\\S+)', log_message)
    request_id = match.group(1) if match else None
    return request_id