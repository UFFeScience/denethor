import re
from denethor_utils import utils as du
from denethor_provenance.database.db_model import *

def parse_message(message, stats_attributes, default_sep):
    """
    Parse the log message field and extract attributes based on the provided stats attributes.

    Args:
        message (str): The log message to parse.
        stats_attributes (dict): The dictionary containing the stats attributes.
        default_sep (str): The default separator to use.

    Returns:
        dict: The parsed attributes as a dictionary.
    """
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
                parsed_message[attribute['fieldName']] = du.parse_int(str_val)
            elif attribute['dataType'] == 'float':
                parsed_message[attribute['fieldName']] = du.parse_float(str_val)
            else:
                parsed_message[attribute['fieldName']] = str_val
        else:
            # If the attribute is not found, store None
            parsed_message[attribute['fieldName']] = None

    return parsed_message


def parse_execution_logs(request_id, logs, default_stats: dict, custom_stats: dict, default_sep: str):
    """
    Parse all the execution logs for the same request id and create a ServiceExecution object.

    Args:
        request_id (str): The request ID.
        logs (list): The list of logs to parse.
        default_stats (dict): The default stats dictionary.
        custom_stats (dict): The custom stats dictionary.
        default_sep (str): The default separator to use if not specified.

    Returns:
        ServiceExecution: The parsed service execution object.
    """
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


def process_default_stats(service_execution, parsed_message: dict, timestamp: int):
    """
    Process the default stats based on the parsed message. The default stats are predefined and are always present.

    Args:
        service_execution (ServiceExecution): The service execution object.
        parsed_message (dict): The parsed message as a dictionary.
        timestamp (int): The timestamp of the log.

    Raises:
        ValueError: If the log type is unknown.
    """
    match parsed_message["logType"]:
        case 'START':
            service_execution.start_time = du.convert_ms_to_datetime(timestamp)
                    
        case 'END':
            service_execution.end_time = du.convert_ms_to_datetime(timestamp)
                    
        case 'REPORT' | 'PRODUCED_FILES_INFO' | 'CONSUMED_FILES_INFO':
            service_execution.update_from_dict(parsed_message)

        case 'FILE_TRANSFER':
            file = File.create_from_dict(parsed_message)
            execution_file = ExecutionFile.create_from_dict(parsed_message)
            execution_file.file = file
            service_execution.execution_files.append(execution_file)
        
        case '_':
            raise ValueError(f"Could not parse message. LogType unknown: {parsed_message['logType']}. LogMessage: {parsed_message['message']}")


def process_custom_stats(service_execution, parsed_message: dict):
    """
    Process the custom stats based on the parsed message. The custom stats are defined by the user for each activity.

    Args:
        service_execution (ServiceExecution): The service execution object.
        parsed_message (dict): The parsed message as a dictionary.
    """
    # Tratamento de "custom_statistics". Elas serão salvas nas tabelas "statistics" e "execution_statistics"
    # O atributo "fieldName" será usado como o nome da estatística no banco e o "dataType" será usado para determinar o tipo de valor a ser salvo
    # iterar por cada estatística adicional, ignorando o atributo "request_id"
    for field_name, value in parsed_message.items():
        if field_name != 'request_id' and field_name != 'logType':
            stat = Statistics(statistics_name=field_name, statistics_description='')
            execution_stat = ExecutionStatistics(statistics=stat)
            if type(value) == int:
                execution_stat.value_integer = value
            elif type(value) == float:
                execution_stat.value_float = value
            elif type(value) == str:
                execution_stat.value_string = value
            
            service_execution.execution_statistics.append(execution_stat)

