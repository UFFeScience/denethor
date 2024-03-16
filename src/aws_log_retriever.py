from utils import log_utils
import time
import boto3

def retrieve_logs_from_aws(params):
    """
    Retrieves logs from AWS Lambda and saves them to a file.

    Args:
        params (dict): A dictionary containing the following parameters:
            - execution_id (str): The execution ID.
            - workflowStartTimeMs (int): The start timestamp in milliseconds.
            - endTimeLogRetrieverMs (int, optional): The end timestamp in milliseconds. Defaults to the current timestamp.
            - functions (list): A list of lambda function names.
            - log_path (str): The path where the logs will be saved.
            - log_file (str): The name of the log file.

    Raises:
        ValueError: If no log records were found.

    Returns:
        None
    """
    # Retrieve logs from AWS Lambda organized by logStreamName
    client = boto3.client('logs')
    
    execution_id = params['execution_id']

    # Set the start and end time for the log filter based on the workflow start time and the current time
    log_filter_start_time_ms = params['workflow_start_time_ms']
    log_filter_end_time_ms = int(time.time() * 1000)

    ############################################################################################################
    # If the 'override_...' parameters are present, then the respective variables are updated with the new values
    # It can be used for testing purposes, or to retrieve logs for a specific time range
    override_start_time_ms = params['override_start_time_ms']
    if override_start_time_ms is not None:
        log_filter_start_time_ms = override_start_time_ms
    
    override_end_time_ms = params['override_end_time_ms']
    if override_end_time_ms is not None:
        log_filter_end_time_ms = override_end_time_ms
    
    override_execution_id = params['override_execution_id']
    if override_execution_id is not None:
        execution_id = override_execution_id
    ############################################################################################################
    
    functions = params['functions']
    log_path = params['log_path']
    log_file = params['log_file']
    
    # file_path = log_path.replace('[execution_id]', execution_id)

    for function_name in functions:
        log_group_name = f"/aws/lambda/{function_name}"
        response = client.filter_log_events(
            logGroupName=log_group_name,
            startTime=log_filter_start_time_ms,
            endTime=log_filter_end_time_ms
        )
        logs = response['events']
        if logs == None or len(logs) == 0:
            raise ValueError("No log records were found!")
        
        file_name = log_file.replace('[function_name]', function_name).replace('[execution_id]', execution_id)
        
        log_utils.save_to_file(logs, log_path, file_name)

        print(f"Logs saved to {log_path}/{file_name} in json format")


# ################################################
# # FOR LOCAL TESTING!!!!
# ################################################
# from datetime import datetime, timezone

# start_time_human = "2024-03-15 02:52:52Z"
# end_time_human   = "2024-03-15 02:53:26Z"

# # Converte a string para um objeto datetime
# start_time_date = datetime.strptime(start_time_human, "%Y-%m-%d %H:%M:%SZ").replace(tzinfo=timezone.utc)
# end_time_date   = datetime.strptime(end_time_human, "%Y-%m-%d %H:%M:%SZ").replace(tzinfo=timezone.utc)

# # Converte para milissegundos e acrescenta uma margem de 10 segundos
# # antes e depois do intervalo para garantir que todos os logs sejam capturados
# override_start_time_ms = int(start_time_date.timestamp() * 1000) - (10 * 1000)
# override_end_time_ms = int(end_time_date.timestamp() * 1000) + (10 * 1000)

# execution_id = 'EXEC_' + str(start_time_date).replace('T', '_').replace('+00:00', '_UTC').replace('-03:00', '_GMT3').replace(':', '-').replace(' ', '_').replace('Z', '')

# # Store workflow configuration and runtime parameters
# workflow_params = {
#     'execution_id': execution_id,
#     'workflow_start_time_str':None,
#     'workflow_start_time_ms': 0,
#     'input_files_name': None,
#     'input_files_path': None
# }

# override_params = {
#     'override_start_time_ms': override_start_time_ms,
#     'override_end_time_ms': override_end_time_ms
# }

# step_params = {
#     "functions": ["tree_constructor", "subtree_mining"],
#     "log_path": "data/executions/logs",
#     "log_file": "log_[function_name]_[execution_id].json"
# }

# params = {
#     **workflow_params,
#     **override_params,
#     **step_params
# }

# retrieve_logs_from_aws(params)