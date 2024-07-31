import time, boto3, datetime, os, json
from denethor_utils import utils as du

# params = {
#             'execution_id': workflow_exec_id,
#             'start_time_ms': start_time_ms,
#             'end_time_ms': end_time_ms,
#             'activity': activity,
#             'execution_env': execution_env,
#             'strategy': strategy,
#             'all_input_data': all_input_data
#         }

def retrieve_logs_from_aws(params):
    """
    Retrieves logs from AWS Lambda and saves them to a file.

    Args:
        params (dict): A dictionary containing the following parameters:
            - execution_id (str): The execution ID.
            - start_time_ms (int): The start timestamp in milliseconds.
            - end_time_ms (int, optional): The end timestamp in milliseconds. Defaults to the current timestamp.
            - activity (list): A list of lambda function names.
            - execution_env: The execution environment configuration.

    Raises:
        ValueError: If no log records were found.

    Returns:
        None
    """
    # Retrieve logs from AWS Lambda organized by logStreamName
    client = boto3.client('logs')
    
    execution_id = params.get('execution_id')

    # Set the start and end time for the log filter based on the workflow start time and the current time
    log_filter_start_time_ms = params.get('start_time_ms')
    log_filter_end_time_ms = params.get('end_time_ms')
    
    if log_filter_end_time_ms is None:
        log_filter_end_time_ms = int(time.time() * 1000)

    function_name = params.get('activity')
    execution_env = params.get('execution_env')
    log_path = execution_env.get('log_config').get('path')
    log_file = execution_env.get('log_config').get('file_name')
    
    log_file = log_file.replace('[activity_name]', function_name).replace('[execution_id]', execution_id)
    
    log_group_name = f"/aws/lambda/{function_name}"
    
    response = client.filter_log_events(
        logGroupName=log_group_name,
        startTime=log_filter_start_time_ms,
        endTime=log_filter_end_time_ms
    )
    logs = response['events']
    if logs == None or len(logs) == 0:
        raise ValueError("No log records were found!")
    
    
    save_log_file(logs, log_path, log_file)

    print(f"Logs saved to {log_path}/{log_file} in json format")



# Save logs to a single file ordered by logStreamName
def save_log_file(json_logs, file_path, file_name):
    # garantir que os logs contenham o campo 'logStreamName' e 'timestamp'
    if not all('logStreamName' in log and 'timestamp' in log for log in json_logs):
        raise ValueError("Logs must contain 'logStreamName' and 'timestamp' fields")
    json_logs.sort(key=lambda x: (x['logStreamName'], x['timestamp']))
    
    # Sanitize file name
    file_name = du.sanitize(file_name)

    # Create the directory if it does not exist
    os.makedirs(file_path, exist_ok=True)

    file = os.path.join(file_path, file_name)
    with open(file=file, mode='w') as file:
        json.dump(json_logs, file, indent=2)
    
    print(f"Logs saved to {file} in json format")



# Define a function to print logs in an organized manner
def print_logs_to_console(logs):
    print("-" * 80)
    for log_item in logs:
        # Convert Unix timestamp to human-readable date and time
        log_datetime = datetime.fromtimestamp(log_item['timestamp'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
        print(f"Timestamp: {log_item['timestamp']}")
        print(f"DateTime: {log_datetime}")
        # print(f"IngestionTime: {item['ingestionTime']}")
        # print(f"EventId: {item['eventId']}")
        print(f"Message: {log_item['message']}")
    print("-" * 80)