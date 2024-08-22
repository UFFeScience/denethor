import time, boto3, datetime, os, json
from denethor_utils import utils as du, env as denv

client = boto3.client('logs')

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
            - log_path (str): The path to save the log files.
            - log_file (str): The name of the log file.

    Raises:
        ValueError: If no log records were found.

    Returns:
        None
    """
    # Retrieve logs from AWS Lambda organized by logStreamName
    execution_id = params.get('execution_id')

    # Set the start and end time for the log filter based on the workflow start time and the current time
    log_filter_start = params.get('start_time_ms')
    log_filter_end = params.get('end_time_ms')
    
    if log_filter_end is None:
        log_filter_end = int(time.time() * 1000)

    activity_name = params.get('activity')
    
    log_path = params.get('log_path')
    log_file = params.get('log_file')
    
    log_file = log_file.replace('[activity_name]', activity_name).replace('[execution_id]', execution_id)
    
    log_group_name = f"/aws/lambda/{activity_name}"
    
    # response = client.filter_log_events(
    #     logGroupName=log_group_name,
    #     startTime=log_filter_start_time_ms,
    #     endTime=log_filter_end_time_ms
    # )
    # logs = response['events']

    logs = get_all_log_events(log_group_name, log_filter_start, log_filter_end)
    if logs == None or len(logs) == 0:
        raise ValueError("No log records were found! log_group_name={log_group_name}, start_time={log_filter_start}, end_time={log_filter_end}")
    
    
    save_log_file(logs, log_path, log_file)

    print(f"Logs for function {activity_name} saved to {log_path}/{log_file} in json format")



def get_all_log_events(log_group_name, start_time, end_time, filter_pattern=""):
    all_events = []
    next_token = None

    # If there are more log events than the limit, the response will contain a 'nextToken' field
    # This token can be used to retrieve the next batch of log events
    while True:
        if next_token:
            response = client.filter_log_events(
                logGroupName=log_group_name,
                startTime=int(start_time),
                endTime=int(end_time),
                filterPattern=filter_pattern,
                nextToken=next_token
            )
        else:
            response = client.filter_log_events(
                logGroupName=log_group_name,
                startTime=int(start_time),
                endTime=int(end_time),
                filterPattern=filter_pattern
            )

        all_events.extend(response['events'])

        next_token = response.get('nextToken')
        if not next_token:
            break

    return all_events



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
    with open(file=file, mode='w', encoding='utf-8') as file:
        json.dump(json_logs, file, ensure_ascii=False, indent=4)
    
    print(f"Logs saved to {file_name} in json format")



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