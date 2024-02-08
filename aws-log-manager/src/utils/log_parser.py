import re
from database.db_model import *
from database.repository import *
from database.conn import *
from utils.log_utils import *

def parse_log_message(message, config_analyzer: dict):
    
    log_type = message.split()[0]
    parsed_message = {}
    # Check if the log type is in the configuration
    if log_type in config_analyzer['basicLogTypes']:
        
        # Prepare a dictionary to store the parsed attributes
        parsed_attributes = {}
        default_separator = config_analyzer['defaultSeparator']
        # Iterate over each attribute
        for attribute in config_analyzer['basicLogTypes'][log_type]:
            
            separator = attribute.get('separator', f'[{default_separator}\n]')
            
            # Use regex to extract the attribute value from the message
            pattern = f'{attribute['searchKey']}:\\s*(.*?){separator}'
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
            'logType': log_type,
            **parsed_attributes
        }

    return parsed_message


def parse_logs(request_id, logs, config_analyzer: dict):
    
    service_execution = ServiceExecution(request_id=request_id)
    
    for log in logs:
        
        service_execution.log_stream_name = log['logStreamName']
        
        parsed_log = parse_log_message(log['message'], config_analyzer)
        
        #   
        # Validations of request_id
        #
        if parsed_log['request_id'] is None:
            raise ValueError(f"Invalid request_id:{parsed_log['request_id']}")
        
        if service_execution.request_id != parsed_log['request_id']:
            raise ValueError(f"Error! Current request_id:{parsed_log['request_id']} | Expected request_id:{service_execution.request_id}")
        
        ##########

        match parsed_log['logType']:
            case 'START':
                # "timestamp": 1705599854279, "message": "START RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c Version: $LATEST\n"
                service_execution.start_time = to_datetime(log['timestamp'])
            
            case 'END':
                # "timestamp": 1705599874327, "message": "END RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\n"
                service_execution.end_time = to_datetime(log['timestamp'])
            
            case 'REPORT':
                process_report(service_execution, parsed_log)
            
            case 'FILE_TRANSFER':
                process_file_transfer(service_execution, parsed_log)
            
            case _:
                a = parsed_log
                print(a)

    return service_execution





# "message": "REPORT RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\tDuration: 1010.14 ms\tBilled Duration: 1011 ms\tMemory Size: 128 MB\tMax Memory Used: 115 MB\tInit Duration: 918.52 ms\t\n"
def process_report(service_execution, log_dict: dict):
    service_execution.duration = parse_float(log_dict['Duration'])
    service_execution.billed_duration = parse_float(log_dict['Billed Duration'])
    service_execution.memory_size = parse_int(log_dict['Memory Size'])
    service_execution.max_memory_used = parse_int(log_dict['Max Memory Used'])
    service_execution.init_duration = parse_float(log_dict['Init Duration'])

AQUIIIIIIIIIIIIIIIIIIIIII
# "message": 'FILE_TRANSFER RequestId: efc97200-d2c8-4523-b469-f4ae7292ada7\t TransferType: consumed\t FileName: ORTHOMCL1490\t Bucket: mribeiro-bucket-input\t FilePath: input/ORTHOMCL1490\t TransferDuration: 279.0652149999886 ms\t FileSize: 5128 bytes\n'
def process_file_transfer(service_execution, log_dict: dict):
    file = File(name=log_dict['name'], size=parse_int(log_dict['size']), path=log_dict['path'], bucket=log_dict['bucket'])
    execution_file = ExecutionFile(transfer_duration=parse_float(log_dict['transfer_duration']), transfer_type=log_dict['transfer_type'], file=file)
    service_execution.execution_files.append(execution_file)
    

# "message": "CONSUMED_FILES_INFO RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t NumFiles: 100 files\t TotalFilesSize: 36777 bytes\t Duration: 6933.13087699994 ms\n"
# "message": "PRODUCED_FILES_INFO RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t NumFiles: 335 files\t TotalFilesSize: 83697 bytes\t Duration: 17168.395734999875 ms\n"
def process_total_file_info(service_execution, log_dict: dict, transfer_type: str):
    if transfer_type == 'consumed':
        service_execution.consumed_files_count = parse_int(log_dict['NumFiles'])
        service_execution.consumed_files_size = parse_int(log_dict['TotalFileSize'])
        service_execution.consumed_files_transfer_duration = parse_float(log_dict['Duration'])
    elif transfer_type == 'produced':
        service_execution.produced_files_count = parse_int(log_dict['NumFiles'])
        service_execution.produced_files_size = parse_int(log_dict['TotalFilesSize'])
        service_execution.produced_files_transfer_duration = parse_float(log_dict['Duration'])

# "message": "SUBTREE_FILES_CREATE RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t Duration: 795.8109850000028 ms\n"
def process_subtree_info(service_execution, log_dict: dict):
    subtree_stat = Statistics(name='subtree_duration', description='Tempo de execução da atividade de criação de subárvores')
    subtree_execution_stat = ExecutionStatistics(statistics=subtree_stat, value_float=parse_float(log_dict['Duration']))
    service_execution.execution_statistics.append(subtree_execution_stat)

# "message": "MAF_DATABASE_CREATE RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t MaxMaf: 5\t Duration: 485681.23013399995 ms\t MafDatabase: {1: {}, 2: {'tree_ORTHOMCL1_Inner3.nexus': ['tree_ORTHOMCL1977_Inner2.nexus', 'tree_ORTHOMCL1977_Inner1.nexus'],      (.......)     , 3: {}, 5: {'tree_ORTHOMCL1_Inner3.nexus': ['tree_ORTHOMCL1977_Inner3.nexus'],) 'tree_ORTHOMCL1977_Inner3.nexus': ['tree_ORTHOMCL1_Inner3.nexus']}}\n"
def process_maf_databse_info(service_execution, log_dict: dict):
    max_maf_stat = Statistics(name='max_maf', description='Maior valor de MAF encontrado no processamento dos arquivos de entrada')
    max_maf_execution_stat = ExecutionStatistics(statistics=max_maf_stat, value_integer=parse_int(log_dict['MaxMaf']))
    service_execution.execution_statistics.append(max_maf_execution_stat)
    
    maf_db_duration_stat = Statistics(name='maf_db_duration', description='Tempo de execução da atividade de criação do banco de dados MAF')
    maf_db_duration_execution_stat = ExecutionStatistics(statistics=maf_db_duration_stat, value_float=parse_float(log_dict['Duration']))
    service_execution.execution_statistics.append(maf_db_duration_execution_stat)
    
    maf_database_stat = Statistics(name='maf_database', description='Valor do dicionário "maf_database" obtido ao término do processo')
    maf_database_execution_stat = ExecutionStatistics(statistics=maf_database_stat, value_string=log_dict['MafDatabase'])
    service_execution.execution_statistics.append(maf_database_execution_stat)

