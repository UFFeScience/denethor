import re
from denethor import constants
from denethor.utils import utils as du
from denethor.core.model import *


def parse_message(message: str, stats_attributes: dict, default_separator: str):
    """
    Parse the log message field and extract attributes based on the provided stats attributes.

    Args:
        message (str): The log message to parse.
        stats_attributes (dict): The dictionary containing the stats attributes.
        default_separator (str): The default separator to use.

    Returns:
        dict: The parsed attributes as a dictionary.
    """
    log_type = find_log_type(message, stats_attributes)

    if not log_type or log_type not in stats_attributes:
        return None

    # Prepare a dictionary to store the parsed attributes
    parsed_message = {"logType": log_type}

    # Iterate over each attribute
    for attribute in stats_attributes[log_type]:

        sep = attribute.get("separator", f"[{default_separator}\n]")
        # Use regex to extract the attribute value from the message
        pattern = f"{attribute['searchKey']}:\\s*(.*?){sep}"
        match = re.search(pattern, message)

        if match:
            # Store the attribute value in the dictionary
            str_val = match.group(1).strip()
            if attribute["dataType"] == "integer":
                parsed_message[attribute["fieldName"]] = du.parse_int(str_val)
            elif attribute["dataType"] == "float":
                parsed_message[attribute["fieldName"]] = du.parse_float(str_val)
            else:
                parsed_message[attribute["fieldName"]] = str_val
        else:
            # If the attribute is not found, store None
            parsed_message[attribute["fieldName"]] = None

    return parsed_message


def parse_execution_logs(
    service_execution: ServiceExecution, logs: list, statistics: dict
) -> None:
    """
    Parse all the execution logs for the same request id and update the ServiceExecution object.

    Args:
        service_execution (ServiceExecution): The service execution object to update.
        logs (list): The list of logs to parse.
        statistics (dict): The dictionary containing the statistics.

    """

    default_stats = statistics["default_statistics"]
    custom_stats = statistics["custom_statistics"]
    default_sep = statistics["default_separator"]

    stats = default_stats | custom_stats

    # iterate over each log in the logs list
    for log in logs:

        parsed_message = parse_message(log["message"], stats, default_sep)

        if not parsed_message:
            print(f"Ignoring log message: {log['message']}")
            continue

        if service_execution.request_id != parsed_message["request_id"]:
            raise ValueError(
                f"Request ID mismatch: {service_execution.request_id} != {parsed_message['request_id']}"
            )

        if service_execution.log_stream_name != log["logStreamName"]:
            raise ValueError(
                f"Log stream name mismatch: {service_execution.log_stream_name} != {log['logStreamName']}"
            )

        if parsed_message["logType"] in default_stats:
            process_default_stats(service_execution, parsed_message, log["timestamp"])

        elif parsed_message["logType"] in custom_stats:
            process_custom_stats(service_execution, parsed_message)

        else:
            raise ValueError(
                f"Could not parse message for activity: {service_execution.activity}. LogType unknown: {parsed_message['logType']}. LogMessage: {log['message']}"
            )

    validate_service_execution(service_execution)


def process_default_stats(
    service_execution: ServiceExecution, parsed_message: dict, timestamp: int
):
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
        case "START":
            service_execution.start_time = du.convert_ms_to_datetime(timestamp)

        case "END":
            service_execution.end_time = du.convert_ms_to_datetime(timestamp)

        case "REPORT" | "PRODUCED_FILES_INFO" | "CONSUMED_FILES_INFO":
            service_execution.update_from_dict(parsed_message)

        case "FILE_TRANSFER":
            file = File.create_from_dict(parsed_message)
            execution_file = ExecutionFile.create_from_dict(parsed_message)
            execution_file.file = file
            service_execution.execution_files.append(execution_file)

        case "_":
            raise ValueError(
                f"Could not parse message. LogType unknown: {parsed_message['logType']}. LogMessage: {parsed_message['message']}"
            )


def process_custom_stats(service_execution: ServiceExecution, parsed_message: dict):
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
        if field_name != "request_id" and field_name != "logType":
            stat = Statistics(statistics_name=field_name, statistics_description="")
            execution_stat = ExecutionStatistics(statistics=stat)
            if type(value) == int:
                execution_stat.value_integer = value
            elif type(value) == float:
                execution_stat.value_float = value
            elif type(value) == str:
                execution_stat.value_string = value

            service_execution.execution_statistics.append(execution_stat)


def find_log_type(message: str, stats_attributes: dict) -> str:
    # verificar o primeiro elemento da mensagem
    first_element = message.split()[0]
    if first_element in stats_attributes:
        return first_element

    # Caso não econtre, procurar no resto da mensagem
    for log_type in stats_attributes.keys():
        if log_type in message:
            return log_type

    return None


def validate_service_execution(service_execution: ServiceExecution):
    """
    Validate the service execution object to ensure all required fields are present.

    Args:
        service_execution (ServiceExecution): The service execution object to validate.

    Raises:
        ValueError: If any required field is missing.
    """
    if not service_execution.request_id:
        raise ValueError(
            "ServiceExecution is missing request_id for: {service_execution}"
        )

    if service_execution.provider_conf.provider.provider_tag == constants.AWS_LAMBDA:
        if not service_execution.start_time:
            raise ValueError(
                "ServiceExecution is missing start_time for: {service_execution}"
            )
        if not service_execution.end_time:
            raise ValueError(
                "ServiceExecution is missing end_time for: {service_execution}"
            )
        if not service_execution.duration:
            raise ValueError(
                "ServiceExecution is missing duration for: {service_execution}"
            )
        if not service_execution.billed_duration:
            raise ValueError(
                "ServiceExecution is missing billed_duration for: {service_execution}"
            )
        if not service_execution.memory_size:
            raise ValueError(
                "ServiceExecution is missing memory_size for: {service_execution}"
            )
        if not service_execution.max_memory_used:
            raise ValueError(
                "ServiceExecution is missing max_memory_used for : {service_execution}"
            )
