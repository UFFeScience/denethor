import re
from database.db_model import *
from database.repository import *
from database.conn import *
from utils.log_utils import *

def parse_message(message, stats_attributes, default_sep):

    log_type = message.split()[0]

    # Prepare a dictionary to store the parsed attributes
    parsed_message = {"logType": log_type}

    # Iterate over each attribute
    for attribute in stats_attributes[log_type]:
        
        sep = attribute.get('separator', f'[{default_sep}\n]')
        # Use regex to extract the attribute value from the message
        pattern = f'{attribute['searchKey']}:\\s*(.*?){sep}'
        match = re.search(pattern, message)
        
        if match:
            # Store the attribute value in the dictionary
            str_val = match.group(1).strip()
            if attribute['dataType'] == 'integer':
                parsed_message[attribute['fieldName']] = parse_int(str_val)
            elif attribute['dataType'] == 'float':
                parsed_message[attribute['fieldName']] = parse_float(str_val)
            else:
                parsed_message[attribute['fieldName']] = str_val
        else:
            # If the attribute is not found, store None
            parsed_message[attribute['fieldName']] = None

    return parsed_message


def parse_logs(request_id, logs, default_stats: dict, custom_stats: dict, default_sep: str):
    
    service_execution = ServiceExecution()
    stats = default_stats | custom_stats

    # iterate over each log in the logs list
    for log in logs:

        service_execution.request_id = request_id
        service_execution.log_stream_name = log['logStreamName']
        
        parsed_message = parse_message(log['message'], stats, default_sep)
        
        if parsed_message["logType"] in default_stats:
            process_default_stats(service_execution, parsed_message, log['timestamp'])

        elif parsed_message["logType"] in custom_stats:
            process_custom_stats(service_execution, parsed_message)
        
        else:
            print("--------------------------------------------------------------------------")
            print(f"Could not parse message. LogType unknown: {parsed_message["logType"]}. LogMessage: {log['message']}")
            print("--------------------------------------------------------------------------")
            
    return service_execution


# "timestamp": 1705599854279, "message": "START RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c Version: $LATEST\n"
# "timestamp": 1705599874327, "message": "END RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\n"
# "message": "REPORT RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\tDuration: 1010.14 ms\tBilled Duration: 1011 ms\tMemory Size: 128 MB\tMax Memory Used: 115 MB\tInit Duration: 918.52 ms\t\n"
# "message": "CONSUMED_FILES_INFO RequestId: 4f71664c-e6ca-4bc3-ae74-3d4e801087d9\t FilesCount: 1 files\t FilesSize: 3500 bytes\t TransferDuration: 316.1569789999987 ms\n",
# "message": "PRODUCED_FILES_INFO RequestId: efc97200-d2c8-4523-b469-f4ae7292ada7\t FilesCount: 1 files\t FilesSize: 347 bytes\t TransferDuration: 357.5239620000019 ms\n",
# "message": "FILE_TRANSFER RequestId: 4f71664c-e6ca-4bc3-ae74-3d4e801087d9\t TransferType: produced\t FileName: tree_ORTHOMCL1042.nexus\t Bucket: mribeiro-bucket-output-tree\t FilePath: tree_ORTHOMCL1042.nexus\t Duration: 295.30242400000617 ms\t FileSize: 405 bytes\n",
def process_default_stats(service_execution, parsed_message: dict, timestamp: int):
    match parsed_message["logType"]:
        case 'START':
            service_execution.start_time = to_datetime(timestamp)
                    
        case 'END':
            service_execution.end_time = to_datetime(timestamp)
                    
        case 'REPORT' | 'PRODUCED_FILES_INFO' | 'CONSUMED_FILES_INFO':
            service_execution.update_from_dict(parsed_message)

        case 'FILE_TRANSFER':
            file = File.create_from_dict(parsed_message)
            execution_file = ExecutionFile.create_from_dict(parsed_message)
            execution_file.file = file
            service_execution.execution_files.append(execution_file)
        
        case '_':
            raise ValueError(f"Could not parse message. LogType unknown: {parsed_message['logType']}. LogMessage: {parsed_message['message']}")


# "message": "SUBTREE_FILES_CREATE RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t Duration: 795.8109850000028 ms\n"
# "message": "MAF_DATABASE_CREATE RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t MaxMaf: 5\t Duration: 485681.23013399995 ms\t MafDatabase: {1: {}, 2: {'tree_ORTHOMCL1_Inner3.nexus': ['tree_ORTHOMCL1977_Inner2.nexus', 'tree_ORTHOMCL1977_Inner1.nexus'],      (.......)     , 3: {}, 5: {'tree_ORTHOMCL1_Inner3.nexus': ['tree_ORTHOMCL1977_Inner3.nexus'],) 'tree_ORTHOMCL1977_Inner3.nexus': ['tree_ORTHOMCL1_Inner3.nexus']}}\n"
def process_custom_stats(service_execution, parsed_message: dict):
    # Tratamento de "customStatistics". Elas serão salvas nas tabelas "statistics" e "execution_statistics"
    # O atributo "fieldName" será usado como o nome da estatística no banco e o "dataType" será usado para determinar o tipo de valor a ser salvo
    # iterar por cada estatística adicional, ignorando o atributo "request_id"
    for field_name, value in parsed_message.items():
        if field_name != 'request_id' and field_name != 'logType':
            stat = Statistics(name=field_name, description='')
            execution_stat = ExecutionStatistics(statistics=stat)
            if type(value) == int:
                execution_stat.value_integer = value
            elif type(value) == float:
                execution_stat.value_float = value
            elif type(value) == str:
                execution_stat.value_string = value
            
            service_execution.execution_statistics.append(execution_stat)

