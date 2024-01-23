import json
import re
import os
from db.db_model import *
from db.repository import *
from db.conn import *
from utils.log_utils import *


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
    'error_message': None
}

tree_sub_find_info = {
    'subtree_duration': None,
    'max_maf': None,
    'maf_db_duration': None,
    'maf_database': None
}

# arquivos "consumidos" e/ou "produzidos" pela atividade
file_info = []

def main():

    # abrindo o arquivo com os logs da AWS salvos no formato json
    with open(LOG_FILE_PATH) as f:
        data = f.readlines()

    request_id_dict = {}

    # iterando sobre todo o conjunto de logs recuperados para separar por request_id
    for line in data:
        line = line.strip('\n\t,[]')
        if not line:
            continue
        log_line = json.loads(line)
        message = log_line.get('message')
        if message:
            encoded_message = message.encode('utf-8', 'ignore').decode('utf-8')
            # se a mensagem do log possuir a tag RequestId -> armazenar no dicionário
            if "RequestId" in encoded_message:
                request_id = re.search('RequestId: (.+?)\\s', message).group(1)
                if request_id not in request_id_dict:
                    request_id_dict[request_id] = []
                request_id_dict[request_id].append(log_line)
    
    # iterando sobre o conjunto de logs de um request_id (cada chamda da função lambda)
    # esse conjunto representa uma execução completa da atividade para um conjunto de arquivos de entrada
    for request_id, logs_list in request_id_dict.items():
        
        for log_item in logs_list:
            process(log_item)
        
        print(execution_info)
        save_to_database()
        
        # zerando os dicionários
        clear(execution_info)
        clear(tree_sub_find_info)
        file_info.clear()

    # log_str = json.dumps(log)
    

def process(log):

    #   
    # Validations of request_id
    #
    message = log.get('message')
    request_id = re.search('RequestId: (.+?)\\s', message).group(1)

    if request_id == None:
        raise ValueError(f"Invalid request_id:{request_id}")
    
    if execution_info['request_id'] != None and execution_info['request_id'] != request_id:
        raise ValueError(f"Error! New request_id:{request_id} | Expected request_id:{execution_info['request_id']}")
    
    execution_info['request_id']  = request_id

    ##########

    #
    # Validations of log_stream_name
    #
    log_stream_name = log.get('logStreamName')

    if log_stream_name == None:
        raise ValueError(f"Invalid log_stream_name:{log_stream_name}")
    
    if execution_info['log_stream_name'] != None and execution_info['log_stream_name'] != log_stream_name:
        raise ValueError(f"Error! New log_stream_name:{log_stream_name} | Expected log_stream_name:{execution_info['log_stream_name']}")
    
    execution_info['log_stream_name'] = log_stream_name
    
    ##########
    
    
    log_type = re.search('^\\w+', message).group(0)

    match log_type:
        # "message":"START RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c Version: $LATEST\n"
        case 'START':
            execution_info['start_time'] = convert_to_datetime(log.get('timestamp'))
        
        # "message":"END RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\n"
        case 'END':
            execution_info['end_time'] = convert_to_datetime(log.get('timestamp'))
        
        # "message":"FILE_DOWNLOAD RequestId: c3df54b6-1da5-48b2-bec4-093b55c96692\t FileName: ORTHOMCL1\t Bucket: mribeiro-bucket-input\t FilePath: data/testset/ORTHOMCL1\t Duration: 407.83485699999744 ms\t FileSize: 1640 bytes\n"
        case 'FILE_DOWNLOAD':
            process_file_info('consumed', message)
        
        # "message":"FILE_UPLOAD RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\t FileName: tree_ORTHOMCL1.nexus\t Bucket: mribeiro-bucket-output-tree\t FilePath: tree_ORTHOMCL1.nexus\t Duration: 292.6312569999965\t FileSize: 339\n"
        case 'FILE_UPLOAD':
            process_file_info('produced', message)
        
        # "message":"CONSUMED_FILES_INFO RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t NumFiles: 100 files\t TotalFilesSize: 36777 bytes\t Duration: 6933.13087699994 ms\n"
        case 'CONSUMED_FILES_INFO':
            process_total_file_info('consumed', message)
        
        # "message": "PRODUCED_FILES_INFO RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t NumFiles: 335 files\t TotalFilesSize: 83697 bytes\t Duration: 17168.395734999875 ms\n"
        case 'PRODUCED_FILES_INFO':
            process_total_file_info('produced', message)
        
        # "message": "SUBTREE_FILES_CREATE RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t Duration: 795.8109850000028 ms\n"
        case 'SUBTREE_FILES_CREATE':
            process_subtree_info(message)
        
        #"message": "MAF_DATABASE_CREATE RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t MaxMaf: 5\t Duration: 485681.23013399995 ms\t MafDatabase: {1: {}, 2: {'tree_ORTHOMCL1_Inner3.nexus': ['tree_ORTHOMCL1977_Inner2.nexus', 'tree_ORTHOMCL1977_Inner1.nexus'],      (.......)     , 3: {}, 5: {'tree_ORTHOMCL1_Inner3.nexus': ['tree_ORTHOMCL1977_Inner3.nexus'],) 'tree_ORTHOMCL1977_Inner3.nexus': ['tree_ORTHOMCL1_Inner3.nexus']}}\n"
        case 'MAF_DATABASE_CREATE':
            process_maf_databse_info(message)
        
        # "REPORT RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\tDuration: 1010.14 ms\tBilled Duration: 1011 ms\tMemory Size: 128 MB\tMax Memory Used: 115 MB\tInit Duration: 918.52 ms\t\n"
        case 'REPORT':
            process_report_info(message)
        
        case _:
            log_type = None


def process_file_info(action_type: str, message):
    file_info.append({
        'name': re.search('FileName: (.+?)\\t', message).group(1),
        'size': re.search('FileSize: (.+?) bytes\\n', message).group(1),
        'path': re.search('FilePath: (.+?)\\t', message).group(1),
        'bucket': re.search('Bucket: (.+?)\\t', message).group(1),
        'transfer_duration': re.search('Duration: (.+?) ms\\t', message).group(1),
        'action_type': action_type
    })

def process_total_file_info(action_type: str, message):
    execution_info[f'num_{action_type}_files'] = re.search('NumFiles: (.+?) files\\t', message).group(1)
    execution_info[f'total_{action_type}_files_size'] = re.search('TotalFilesSize: (.+?) bytes\\t', message).group(1)
    execution_info[f'total_{action_type}_transfer_duration'] = re.search('Duration: (.+?) ms\\n', message).group(1)
    

def process_subtree_info(message):
    tree_sub_find_info['subtree_duration'] = re.search('Duration: (.+?) ms\\n', message).group(1)

def process_maf_databse_info(message):
    tree_sub_find_info['max_maf'] = re.search('MaxMaf: (.+?)\\t', message).group(1)
    tree_sub_find_info['maf_db_duration'] = re.search('Duration: (.+?) ms\\t', message).group(1)
    tree_sub_find_info['maf_database'] = re.search('MafDatabase: (.+?)\\n', message).group(1)


def process_report_info(message):
    execution_info['duration'] = re.search('Duration: (.+?) ms\\t', message).group(1)
    execution_info['billed_duration'] = re.search('Billed Duration: (.+?) ms\\t', message).group(1)
    execution_info['memory_size'] = re.search('Memory Size: (.+?) MB\\t', message).group(1)
    execution_info['max_memory_used'] = re.search('Max Memory Used: (.+?) MB\\t', message).group(1)
    # Verificar se o atributo "Init Duration" existe
    match = re.search('Init Duration: (.+?) ms\\t', message)
    if match:
        execution_info['init_duration'] = match.group(1)






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
                'value_float': tree_sub_find_info['subtree_duration']
            }
        )
        print(f'{'Saving' if created else 'Retrieving'} Subtree Duration info: {subtree_duration.value_float}')

        # maf_db_duration
        maf_db_duration, created = execution_statistics_repo.get_or_create(
            {
                'service_execution_id': service_execution.id,
                'statistics_id': stat_maf_db_duration.id,
                'value_float': tree_sub_find_info['maf_db_duration']
            }
        )
        print(f'{'Saving' if created else 'Retrieving'} Maf DB Duration info: {maf_db_duration.value_float}')

        # max_maf
        max_maf, created = execution_statistics_repo.get_or_create(
            {
                'service_execution_id': service_execution.id,
                'statistics_id': stat_max_maf.id,
                'value_integer': tree_sub_find_info['max_maf']
            }
        )
        print(f'{'Saving' if created else 'Retrieving'} Maf DB Duration info: {max_maf.value_integer}')

        # maf_database
        maf_database, created = execution_statistics_repo.get_or_create(
            {
                'service_execution_id': service_execution.id,
                'statistics_id': stat_maf_database.id,
                'value_string': tree_sub_find_info['maf_database']
            }
        )
        print(f'{'Saving' if created else 'Retrieving'} Maf Database Dict info: {maf_database.value_string}')


    print(f'Finished saving Service Execution info to Database: [{service_execution.id}]={workflow_activity.name}')
    print(f'\n\n')

if __name__ == "__main__":
    main()