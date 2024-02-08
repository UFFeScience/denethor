import re
from database.db_model import *
from database.repository import *
from database.conn import *
from utils.log_utils import *

def parse_message(message, statistics_dict, separator):
    stat_type = message.split()[0]
    parsed_message = None
    # Check if the log type is in the configuration
    if stat_type in statistics_dict:
        
        # Prepare a dictionary to store the parsed attributes
        parsed_attributes = {}

        # Iterate over each attribute
        for attribute in statistics_dict[stat_type]:
            
            sep = attribute.get('separator', f'[{separator}\n]')
            # Use regex to extract the attribute value from the message
            pattern = f'{attribute['searchKey']}:\\s*(.*?){sep}'
            match = re.search(pattern, message)
            
            if match:
                # Store the attribute value in the dictionary
                str_val = match.group(1).strip()
                if attribute['dataType'] == 'integer':
                    parsed_attributes[attribute['fieldName']] = parse_int(str_val)
                elif attribute['dataType'] == 'float':
                    parsed_attributes[attribute['fieldName']] = parse_float(str_val)
                else:
                    parsed_attributes[attribute['fieldName']] = str_val
            else:
                # If the attribute is not found, store None
                parsed_attributes[attribute['fieldName']] = None

        # Store the parsed log and attributes in the log dictionary
        parsed_message = {
            'statType': stat_type,
            **parsed_attributes
        }

    return parsed_message


def parse_logs(logs, statistics: dict, default_separator: str):
    
    service_execution = ServiceExecution()

    for log in logs:
        service_execution.log_stream_name = log['logStreamName']
        
        parsed_log = parse_message(log['message'], statistics, default_separator)
        
        # caso não tenha conseguido parsear a mensagem, pular para o próximo log
        if parsed_log is None:
            print("--------------------------------------------------------------------------")
            print(f"Could not parse message: {log['message']}")
            print("--------------------------------------------------------------------------")
            continue

        request_id = parsed_log['request_id']

        #   
        # Validations of request_id
        #
        if request_id is None:
            raise ValueError(f"Invalid request_id:{request_id}")
        
        # Atribuir o request_id ao objeto service_execution na primeira vez que ele for encontrado
        if service_execution.request_id is None:
            service_execution.request_id = request_id

        # Validar se o request_id do log atual é o mesmo que o request_id do objeto service_execution
        if service_execution.request_id != request_id:
            raise ValueError(f"Error! Current request_id:{request_id} | Expected request_id:{service_execution.request_id}")
        
        ##########

        # defaultStatistics
        match parsed_log['statType']:
            
            # "timestamp": 1705599854279, "message": "START RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c Version: $LATEST\n"
            case 'START':
                service_execution.start_time = to_datetime(log['timestamp'])
            
            # "timestamp": 1705599874327, "message": "END RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\n"
            case 'END':
                service_execution.end_time = to_datetime(log['timestamp'])
            
            # "message": "REPORT RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\tDuration: 1010.14 ms\tBilled Duration: 1011 ms\tMemory Size: 128 MB\tMax Memory Used: 115 MB\tInit Duration: 918.52 ms\t\n"
            # "message": "CONSUMED_FILES_INFO RequestId: 4f71664c-e6ca-4bc3-ae74-3d4e801087d9\t FilesCount: 1 files\t FilesSize: 3500 bytes\t TransferDuration: 316.1569789999987 ms\n",
            # "message": "PRODUCED_FILES_INFO RequestId: efc97200-d2c8-4523-b469-f4ae7292ada7\t FilesCount: 1 files\t FilesSize: 347 bytes\t TransferDuration: 357.5239620000019 ms\n",
            case 'REPORT' | 'PRODUCED_FILES_INFO'| 'CONSUMED_FILES_INFO':
                service_execution.update_from_dict(parsed_log)

            # "message": "FILE_TRANSFER RequestId: 4f71664c-e6ca-4bc3-ae74-3d4e801087d9\t TransferType: produced\t FileName: tree_ORTHOMCL1042.nexus\t Bucket: mribeiro-bucket-output-tree\t FilePath: tree_ORTHOMCL1042.nexus\t Duration: 295.30242400000617 ms\t FileSize: 405 bytes\n",
            case 'FILE_TRANSFER':
                file = File.create_from_dict(parsed_log)
                execution_file = ExecutionFile.create_from_dict(parsed_log)
                execution_file.file = file
                service_execution.execution_files.append(execution_file)
            
            # Tratamento de "additionalStatistics". Elas serão salvas nas tabelas "statistics" e "execution_statistics"
            # O atributo "fieldName" será usado como o nome da estatística no banco e o "dataType" será usado para determinar o tipo de valor a ser salvo
            case _:
                
                # iterar por cada estatística adicional, ignorando o atributo "request_id"
                for stat_name, stat_value in parsed_log.items():
                    if stat_name != 'request_id':
                        stat = Statistics(name=stat_name, description=f'Estatística adicional')
                        execution_stat = ExecutionStatistics(statistics=stat, value=stat_value, dataType="")
                        service_execution.execution_statistics.append(execution_stat)

                
                # additional_stat = Statistics(name=parsed_log[], description='Tempo de execução da atividade de criação de subárvores')
                # subtree_execution_stat = ExecutionStatistics(statistics=subtree_stat, value_float=parse_float(parsed_log['Duration']))
                # service_execution.execution_statistics.append(subtree_execution_stat)

    return service_execution





# def process_report(service_execution, log_dict: dict):
#     service_execution.duration = parse_float(log_dict['Duration'])
#     service_execution.billed_duration = parse_float(log_dict['Billed Duration'])
#     service_execution.memory_size = parse_int(log_dict['Memory Size'])
#     service_execution.max_memory_used = parse_int(log_dict['Max Memory Used'])
#     service_execution.init_duration = parse_float(log_dict['Init Duration'])

# "message": "FILE_TRANSFER RequestId: 4f71664c-e6ca-4bc3-ae74-3d4e801087d9\t TransferType: produced\t FileName: tree_ORTHOMCL1042.nexus\t Bucket: mribeiro-bucket-output-tree\t FilePath: tree_ORTHOMCL1042.nexus\t Duration: 295.30242400000617 ms\t FileSize: 405 bytes\n",
# def process_file_transfer(service_execution, parsed_log: dict):
#     file = File(name=parsed_log['name'], size=parsed_log['size'], path=parsed_log['path'], bucket=parsed_log['bucket'])
#     execution_file = ExecutionFile(transfer_duration=parsed_log['transfer_duration'], transfer_type=parsed_log['transfer_type'], file=file)
#     service_execution.execution_files.append(execution_file)
    
# def process_consumed_files_info(service_execution, parsed_log: dict):
    # service_execution.consumed_files_count = log_dict['consumed_files_count']
    # service_execution.consumed_files_size = log_dict['consumed_files_size']
    # service_execution.consumed_files_transfer_duration = log_dict['consumed_files_transfer_duration']

# def process_produced_files_info(service_execution, parsed_log: dict):
#     service_execution.produced_files_count = parsed_log['produced_files_count']
#     service_execution.produced_files_size = parsed_log['produced_files_size']
#     service_execution.produced_files_transfer_duration = parsed_log['produced_files_transfer_duration']

# "message": "SUBTREE_FILES_CREATE RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t Duration: 795.8109850000028 ms\n"
def process_subtree_info(service_execution, parsed_log: dict):
    subtree_stat = Statistics(name='subtree_duration', description='Tempo de execução da atividade de criação de subárvores')
    subtree_execution_stat = ExecutionStatistics(statistics=subtree_stat, value_float=parse_float(parsed_log['Duration']))
    service_execution.execution_statistics.append(subtree_execution_stat)

# "message": "MAF_DATABASE_CREATE RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t MaxMaf: 5\t Duration: 485681.23013399995 ms\t MafDatabase: {1: {}, 2: {'tree_ORTHOMCL1_Inner3.nexus': ['tree_ORTHOMCL1977_Inner2.nexus', 'tree_ORTHOMCL1977_Inner1.nexus'],      (.......)     , 3: {}, 5: {'tree_ORTHOMCL1_Inner3.nexus': ['tree_ORTHOMCL1977_Inner3.nexus'],) 'tree_ORTHOMCL1977_Inner3.nexus': ['tree_ORTHOMCL1_Inner3.nexus']}}\n"
def process_maf_databse_info(service_execution, parsed_log: dict):
    max_maf_stat = Statistics(name='max_maf', description='Maior valor de MAF encontrado no processamento dos arquivos de entrada')
    max_maf_execution_stat = ExecutionStatistics(statistics=max_maf_stat, value_integer=parse_int(parsed_log['MaxMaf']))
    service_execution.execution_statistics.append(max_maf_execution_stat)
    
    maf_db_duration_stat = Statistics(name='maf_db_duration', description='Tempo de execução da atividade de criação do banco de dados MAF')
    maf_db_duration_execution_stat = ExecutionStatistics(statistics=maf_db_duration_stat, value_float=parse_float(parsed_log['Duration']))
    service_execution.execution_statistics.append(maf_db_duration_execution_stat)
    
    maf_database_stat = Statistics(name='maf_database', description='Valor do dicionário "maf_database" obtido ao término do processo')
    maf_database_execution_stat = ExecutionStatistics(statistics=maf_database_stat, value_string=parsed_log['MafDatabase'])
    service_execution.execution_statistics.append(maf_database_execution_stat)
