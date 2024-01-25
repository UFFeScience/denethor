import json
import re
import os
from db.db_model import *
from db.repository import *
from db.conn import *
from utils.log_utils import *
from utils.log_parser import *


# FUNCTION_NAME = 'tree_constructor'
FUNCTION_NAME = 'tree_sub_find'
LOG_FILE_PATH = os.path.join('aws-log-manager', '_logs', f'logs_{FUNCTION_NAME}.json')

# estatísticas da execução do serviço
execution_info = {
    'request_id': None,
    'activity_id': None,
    'service_id': None,
    'log_stream_name': None,
    'start_time': None,
    'end_time': None,
    'duration': None,
    'billed_duration': None,
    'init_duration': None,
    'memory_size': None,
    'max_memory_used': None,
    'num_consumed_files': None,
    'num_produced_files': None,
    'total_consumed_files_size': None,
    'total_produced_files_size': None,
    'total_consumed_transfer_duration': None,
    'total_produced_transfer_duration': None,
    'error_message': None,
    'file_info': [],  # arquivos "consumidos" e/ou "produzidos" pela atividade
    'other_stats_info': {
        'subtree_duration': None,
        'max_maf': None,
        'maf_db_duration': None,
        'maf_database': None
    }
}




def main():

    # abrindo o arquivo com os logs da AWS salvos no formato json
    with open(LOG_FILE_PATH) as f:
        logs_data = json.load(f)

    
    # filtrar os registros de log que contem um RequestId no campo message
    # para facilitar o tratamento dos dados 
    # cada conjunto de logs com o mesmo RequestId representa uma execução completa 
    # da atividade para um conjunto de arquivos de entrada
    request_id_dict = get_logs_by_request_id(logs_data)
    
    # iterando sobre o conjunto de logs  um request_id (uma execução da função lambda)
    for request_id, log_itens in request_id_dict.items():
        
        parse_logs(request_id, log_itens)
        
        print(execution_info)
        # save_to_database()
    
        # zerando os dicionários
        clear(execution_info)
        clear(other_stats_info)
        file_info.clear()

    



def save_to_database():
    
    print(f"--------------------------------------------")
    print(f'Saving Execution info to Database...')
    print(f"--------------------------------------------")
    session = Connection().get_session()
   
    # Instânciando as classes de repositórios
    service_provider_repo = ServiceProviderRepository(session)
    workflow_activity_repo = WorkflowActivityRepository(session)
    service_execution_repo = ServiceExecutionRepository(session)
    file_repo = FileRepository(session)
    execution_files_repo = ExecutionFilesRepository(session)
    statistics_repo = StatisticsRepository(session)
    execution_statistics_repo = ExecutionStatisticsRepository(session)


    # Buscando no banco os dados básicos do modelo (dados pré-existentes)
    service_provider = service_provider_repo.get_by_attributes({'name': 'AWS Lambda'})
    execution_info['service_id'] = service_provider.id
    
    workflow_activity = workflow_activity_repo.get_by_attributes({'name': FUNCTION_NAME})
    execution_info['activity_id'] = workflow_activity.id

    
    # verificar se os registros presentes no Log já estão cadastrados na base
    # caso positivo -> apenas recupera o registro
    # caso negativo -> realiza a inclusão e retorna o novo registro

    service_execution, created = service_execution_repo.get_or_create(execution_info)
    print(f'{'Saving' if created else 'Retrieving'} Service Execution info: [{service_execution.id}]={workflow_activity.name} ({service_execution.duration} ms)')

    for item in file_info:
        file_dict = {
            'name': item['name'],
            'size': item['size'],
            'path': item['path'],
            'bucket': item['bucket']
        }
        file, created = file_repo.get_or_create(file_dict)

        execution_file_dict = {
            'service_execution_id': service_execution.id,
            'file_id': file.id,
            'transfer_duration': item['transfer_duration'],
            'action_type': item['action_type']
        }
        execution_file, created = execution_files_repo.get_or_create(execution_file_dict)
        
        print(f'{'Saving' if created else 'Retrieving'} File info: {file} || {'Saving' if created else 'Retrieving'} Execution File info: {execution_file}')


    # para a execução da função 'tree_sub_find', temos estatísticas adicionais para armazenar
    if FUNCTION_NAME == 'tree_sub_find':
        stat_subtree_duration = statistics_repo.get_by_attributes({'name': 'subtree_duration'})
        stat_maf_db_duration = statistics_repo.get_by_attributes({'name': 'maf_db_duration'})
        stat_max_maf = statistics_repo.get_by_attributes({'name': 'max_maf'})
        stat_maf_database = statistics_repo.get_by_attributes({'name': 'maf_database'})
        
        # subtree_duration
        subtree_duration, created = execution_statistics_repo.get_or_create(
            {
                'service_execution_id': service_execution.id,
                'statistics_id': stat_subtree_duration.id,
                'value_float': other_stats_info['subtree_duration']
            }
        )
        print(f'{'Saving' if created else 'Retrieving'} Subtree Duration info: {subtree_duration.value_float}')

        # maf_db_duration
        maf_db_duration, created = execution_statistics_repo.get_or_create(
            {
                'service_execution_id': service_execution.id,
                'statistics_id': stat_maf_db_duration.id,
                'value_float': other_stats_info['maf_db_duration']
            }
        )
        print(f'{'Saving' if created else 'Retrieving'} Maf DB Duration info: {maf_db_duration.value_float}')

        # max_maf
        max_maf, created = execution_statistics_repo.get_or_create(
            {
                'service_execution_id': service_execution.id,
                'statistics_id': stat_max_maf.id,
                'value_integer': other_stats_info['max_maf']
            }
        )
        print(f'{'Saving' if created else 'Retrieving'} Maf DB Duration info: {max_maf.value_integer}')

        # maf_database
        maf_database, created = execution_statistics_repo.get_or_create(
            {
                'service_execution_id': service_execution.id,
                'statistics_id': stat_maf_database.id,
                'value_string': other_stats_info['maf_database']
            }
        )
        print(f'{'Saving' if created else 'Retrieving'} Maf Database Dict info: {maf_database.value_string}')


    print(f'Finished saving Service Execution info to Database: [{service_execution.id}]={workflow_activity.name}')
    print(f'\n\n')

if __name__ == "__main__":
    main()