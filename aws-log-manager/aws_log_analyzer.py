from utils.log_utils import *
from utils.log_parser import *
from utils.read_config import * 
from db.db_model import *
from db.repository import *
from db.conn import *
import json
import os


# Carregar o arquivo JSON
with open('aws-log-manager/config.json') as f:
    config_data = json.load(f)

function_data = choose_function(config_data, pre_choice=1)

file_path = os.path.join(function_data['baseFilePath'], f'logs_{function_data['functionName']}_{function_data['startTime']}.json')
file_path = sanitize(file_path)
# abrindo o arquivo com os logs da AWS salvos no formato json
with open(file_path) as f:
    logs_data = json.load(f)


# filtrar os registros de log que contem um RequestId no campo message
# para facilitar o tratamento dos dados 
# cada conjunto de logs com o mesmo RequestId representa uma execução completa 
# da atividade para um conjunto de arquivos de entrada
request_id_dict = get_logs_by_request_id(logs_data)

# iterando sobre o conjunto de logs  um request_id (uma execução da função lambda)
for request_id, log_itens in request_id_dict.items():
    
    service_execution = process_logs(request_id, log_itens, config_data)
    
    # print(service_execution)

    print(f"--------------------------------------------------------------------------")
    print(f'Saving Execution info of {function_data['functionName']} to Database...')
    print(f'RequestId: {service_execution.request_id}')
    print(f"--------------------------------------------------------------------------")

    session = Connection().get_session()

    #Salvando no Banco de Dados
    # Instânciando as classes de repositórios
    service_provider_repo = ServiceProviderRepository(session)
    workflow_activity_repo = WorkflowActivityRepository(session)
    service_execution_repo = ServiceExecutionRepository(session)
    file_repo = FileRepository(session)
    execution_file_repo = ExecutionFileRepository(session)
    statistics_repo = StatisticsRepository(session)
    execution_statistics_repo = ExecutionStatisticsRepository(session)


    # Buscando no banco os dados básicos do modelo (dados pré-existentes)
    service_provider = service_provider_repo.get_by_attributes({'name': 'AWS Lambda'})
    service_execution.service = service_provider

    workflow_activity = workflow_activity_repo.get_by_attributes({'name': function_data['functionName']})
    service_execution.activity = workflow_activity

    # verificar se os registros presentes no Log já estão cadastrados na base
    # caso positivo -> apenas recupera o registro
    # caso negativo -> realiza a inclusão e retorna o novo registro
    service_execution_db, created = service_execution_repo.get_or_create(service_execution)
    print(f'{'Saving' if created else 'Retrieving'} Service Execution info: [{service_execution_db.id}]={workflow_activity.name} ({service_execution_db.duration} ms)')

    # para cada arquivo de entrada e registro de execução do arquivo,
    # verificamos se ambos já estão cadastrados na base
    for  ef in service_execution.execution_files:
        file_db, file_created = file_repo.get_or_create(ef.file)
        
        ef.service_execution = service_execution_db
        ef.file = file_db
        ef_db, ef_created = execution_file_repo.get_or_create(ef)
        print(f'{'Saving' if file_created else 'Retrieving'} File: {file_db} | {'Saving' if ef_created else 'Retrieving'} Execution_File: {ef_db}')

    # para a execução da função verificamos se existem estatísticas adicionais para armazenar
    for  es in service_execution.execution_statistics:
        statistics_db, stat_created = statistics_repo.get_or_create(es.statistics)
        
        es.service_execution = service_execution_db
        es.statistics = statistics_db
        es_db, es_created = execution_statistics_repo.get_or_create(es)
        print(f'{'Saving' if stat_created else 'Retrieving'} Statistics: {statistics_db} | {'Saving' if es_created else 'Retrieving'} Execution Statistics info: {es_db}')
        
        
    print(f'Finished saving Service Execution info to Database: {service_execution_db}')
    print(f'\n\n')