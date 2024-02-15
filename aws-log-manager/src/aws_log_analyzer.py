from utils.log_utils import *
from utils.log_parser import *
from utils.read_config import * 
from database.db_model import *
from database.repository import *

import json
import os

# Carregar os arquivos JSON
with open('config/execution_info.json') as f:
    EXECUTION_INFO = json.load(f)

with open('config/workflow_activities_info.json') as f: 
    WORKFLOW_INFO = json.load(f)



# Buscando dados básicos do modelo no arquivo de informação da execução e
# salvando no banco de dados, caso não existam
    
# Service Provider
provider = WORKFLOW_INFO['serviceProvider']
provider_model = ServiceProvider.create_from_dict(provider)
provider_db, provider_created = service_provider_repo.get_or_create(provider_model)
print(f'{"Saving" if provider_created else "Retrieving"} Provider: {provider_db}')

# Workflow
workflow = WORKFLOW_INFO['workflow']
workflow_model = Workflow.create_from_dict(workflow)
workflow_db, workflow_created = workflow_repo.get_or_create(workflow_model)
print(f'{"Saving" if workflow_created else "Retrieving"} Workflow: {workflow_db}')

# Workflow Activity
activity = next(act for act in WORKFLOW_INFO['activities'] if act['name'] == EXECUTION_INFO['activityName'])
activity_model = WorkflowActivity.create_from_dict(activity)
activity_model.workflow = workflow_db
activity_db, activity_created = workflow_activity_repo.get_or_create(activity_model)
print(f'{"Saving" if activity_created else "Retrieving"} Activity: {activity_db}')

default_stats = WORKFLOW_INFO['defaultStatistics']
custom_stats = activity['customStatistics']
default_sep = WORKFLOW_INFO['defaultLogMessageSeparator']

# Custom Statistics: iterando sobre as estatísticas customizadas e adicionando ao banco de dados
for log_type in custom_stats:
    for stat in custom_stats[log_type]:
        if stat['fieldName'] != 'request_id':
            stat_model = Statistics(name=stat['fieldName'], description=stat['description'])
            stat_db, stat_created = statistics_repo.get_or_create(stat_model)
            print(f'{"Saving" if stat_created else "Retrieving"} Statistics: {stat_db}')

# abrindo o arquivo com os logs da AWS salvos no formato json
with open(EXECUTION_INFO['logFile']) as f:
    log_data = json.load(f)

# filtra e organiza os registros de log por RequestId 
# cada conjunto representa uma execução completa da atividade para um conjunto de arquivos de entrada
logs_by_request = group_logs_by_request(log_data)

# iterando sobre o conjunto de logs  um request_id (uma execução da função lambda)
for request_id, logs in logs_by_request.items():
    
    print(f"--------------------------------------------------------------------------")
    print(f'Parsing Logs of {activity_db.name} | RequestId: {request_id}')
    print(f"--------------------------------------------------------------------------")

    service_execution = parse_logs(request_id, logs, default_stats, custom_stats, default_sep)
    
    service_execution.provider = provider_db
    service_execution.activity = activity_db
    
    # print(service_execution)

    
    print(f"--------------------------------------------------------------------------")
    print(f'Saving Execution info of {activity_db.name} | RequestId: {request_id} to Database...')
    print(f"--------------------------------------------------------------------------")


    # verificar se os registros presentes no Log já estão cadastrados na base
    # caso positivo -> apenas recupera o registro
    # caso negativo -> realiza a inclusão e retorna o novo registro
    service_execution_db, provider_created = service_execution_repo.get_or_create(service_execution)
    print(f'{'Saving' if provider_created else 'Retrieving'} Service Execution info: [{service_execution_db.id}]={activity_db.name} ({service_execution_db.duration} ms)')

    # para cada arquivo de entrada e registro de execução do arquivo,
    # verificamos se ambos já estão cadastrados na base
    for  exec_file in service_execution.execution_files:
        file_db, file_created = file_repo.get_or_create(exec_file.file)
        
        exec_file.service_execution = service_execution_db
        exec_file.file = file_db
        exec_file_db, exec_file_created = execution_file_repo.get_or_create(exec_file)
        print(f'{'Saving' if file_created else 'Retrieving'} File: {file_db} | {'Saving' if exec_file_created else 'Retrieving'} Execution_File: {exec_file_db}')

    # para a execução da função verificamos se existem estatísticas adicionais para armazenar
    for  exec_stat in service_execution.execution_statistics:
        # nesse ponto assumimos que a estatística já foi incluída no banco de dados
        statistics_db = statistics_repo.get_by_name(exec_stat.statistics.name)
        if not statistics_db:
            raise ValueError(f"Statistics {exec_stat.statistics.name} not found in Database!")
        exec_stat.statistics = statistics_db
        exec_stat.service_execution = service_execution_db
        exec_stat_db, exec_stat_created = execution_statistics_repo.get_or_create(exec_stat)
        print(f'Retrieving Statistics: {statistics_db} | {'Saving' if exec_stat_created else 'Retrieving'} Execution Statistics info: {exec_stat_db}')
        
        
    print(f'Finished saving Service Execution info to Database: {service_execution_db}')
    print(f'\n\n')