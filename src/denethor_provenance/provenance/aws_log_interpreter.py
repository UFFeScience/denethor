from . import log_parser  as parser
from denethor_provenance.database.db_model import *
from denethor_provenance.database.repository import *
from denethor_utils import utils

from datetime import datetime
import json, os, re

def process_and_save_logs(params):
    """
    Analyzes logs based on the provided parameters.

    Args:
        params (dict): A dictionary containing the parameters for log analysis.
            - execution_id (str): The execution ID.
            - functions (list): A list of function names.
            - log_path (str): The path to the log files.
            - log_file (str): The log file name template.
            - provider (dict): Information about the service provider.
            - workflow (dict): Information about the workflow.

    Raises:
        ValueError: If the activity is not found in the workflow activities JSON file.
    
    Returns:
        None
    """
    # Workflow runtime parameters
    execution_id = params['execution_id']

    ############################################################################################################
    # If the 'override_...' parameters are present, then the respective variables are updated with the new values
    # It can be used for testing purposes, or to retrieve logs for a specific time range
    override_execution_id = params['override_execution_id']
    if override_execution_id is not None:
        execution_id = override_execution_id
    ############################################################################################################

    
    # Step params
    functions = params['functions']
    log_path = params['log_path']
    log_file = params['log_file']

    workflow_dict = params['workflow']
    activities_dict = workflow_dict['activities']
    default_separator = workflow_dict['default_separator']
    general_statistics = workflow_dict['general_statistics']


    # Workflow Activity
    for func_name in functions:

        # Finding the corresponding activity in the workflow activities JSON file
        activity = next((act for act in activities_dict if act['activity_name'] == func_name), None)
        if not activity:
            raise ValueError(f"Activity {func_name} not found in the workflow activities JSON file")
        
        activity_name = activity['activity_name']

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
        
        # Opening the log file for the activity, in json format
        file_name = log_file.replace('[function_name]', activity_name).replace('[execution_id]', execution_id)
        file = os.path.join(log_path, file_name)
        with open(file) as f:
            log_data = json.load(f)

        # Filters and organizes log records by RequestId
        # Each set represents a complete execution of the activity for a set of input files
        logs_by_request = group_logs_by_request(log_data)

        activity_custom_statistics = activity['custom_statistics']
        
        # Iterating over the set of logs for a request_id (an execution of the lambda function)
        for request_id, logs in logs_by_request.items():
            
            print(f"--------------------------------------------------------------------------")
            print(f'Parsing Logs of {activity_db.activity_name} | RequestId: {request_id}')
            print(f"--------------------------------------------------------------------------")

            service_execution = parser.parse_execution_logs(request_id, logs, general_statistics, activity_custom_statistics, default_separator)
            
            service_execution.provider = provider_db
            service_execution.activity = activity_db
            
            # print(service_execution)

            
            print(f"--------------------------------------------------------------------------")
            print(f'Saving Execution info of {activity_db.activity_name} | RequestId: {request_id} to Database...')
            print(f"--------------------------------------------------------------------------")


            # verificar se os registros presentes no Log já estão cadastrados na base
            # caso positivo -> apenas recupera o registro
            # caso negativo -> realiza a inclusão e retorna o novo registro
            service_execution_db, provider_created = service_execution_repo.get_or_create(service_execution)
            print(f'{"Saving" if provider_created else "Retrieving"} Service Execution info: [{service_execution_db.se_id}]={activity_db.activity_name} ({service_execution_db.duration} ms)')

            # para cada arquivo de entrada e registro de execução do arquivo,
            # verificamos se ambos já estão cadastrados na base
            for exec_file in service_execution.execution_files:
                file_db, file_created = file_repo.get_or_create(exec_file.file)
                
                exec_file.service_execution = service_execution_db
                exec_file.file = file_db
                exec_file_db, exec_file_created = execution_file_repo.get_or_create(exec_file)
                print(f'{"Saving" if file_created else "Retrieving"} File: {file_db} | {"Saving" if exec_file_created else "Retrieving"} Execution_File: {exec_file_db}')

            # para a execução da função verificamos se existem estatísticas adicionais para armazenar
            for  exec_stat in service_execution.execution_statistics:
                # nesse ponto assumimos que a estatística já foi incluída no banco de dados
                statistics_db = statistics_repo.get_by_name(exec_stat.statistics.statistics_name)
                if not statistics_db:
                    raise ValueError(f"Statistics {exec_stat.statistics.name} not found in Database!")
                exec_stat.statistics = statistics_db
                exec_stat.service_execution = service_execution_db
                exec_stat_db, exec_stat_created = execution_statistics_repo.get_or_create(exec_stat)
                print(f'Retrieving Statistics: {statistics_db} | {"Saving" if exec_stat_created else "Retrieving"} Execution Statistics info: {exec_stat_db}')
                
                
            print(f'Finished saving Service Execution info to Database: {service_execution_db}')
            print(f'\n\n')



# Agrupando logs pelo valor de 'RequestId' no campo 'message' 
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