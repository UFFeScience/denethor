import os, json, time, boto3, datetime
from denethor.utils import utils as du

def retrieve_logs_from_aws(execution_id: str, 
                           function_name: str, 
                           start_time_ms: int, 
                           end_time_ms: int, 
                           log_path: str, 
                           log_file: str):
    """
    Retrieves logs from AWS Lambda and saves them to a file.

    Args:
        execution_id (str): The execution ID of the workflow.
        function_name (str): The name of the Lambda function.
        start_time_ms (int): The start time of the log retrieval interval in milliseconds.
        end_time_ms (int): The end time of the log retrieval interval in milliseconds.
        log_path (str): The path where the log file will be saved.
        log_file (str): The name of the log file.

    Raises:
        ValueError: If no log records were found.

    Returns:
        None
    """
    log_group_name = f"/aws/lambda/{function_name}"
    
    logs = get_all_log_events(log_group_name, start_time_ms, end_time_ms)
    
    if logs == None or len(logs) == 0:
        raise ValueError("No log records were found! log_group_name={log_group_name}, start_time={log_filter_start}, end_time={log_filter_end}")
    
    log_file = log_file.replace('[activity_name]', function_name).replace('[execution_id]', execution_id)
    
    save_log_file(logs, log_path, log_file)

    print(f"Logs for function {function_name} saved to {log_path}/{log_file} in json format")



def get_all_log_events(log_group_name: str,
                        start_time_ms: int,
                        end_time_ms: int,
                        filter_pattern: str =""):

    client = boto3.client('logs')

    all_events = []
    next_token = None

    if not end_time_ms:
        end_time_ms = int(time.time() * 1000)

    # If there are more log events than the limit, the response will contain a 'nextToken' field
    # This token can be used to retrieve the next batch of log events
    while True:
        if next_token:
            response = client.filter_log_events(
                logGroupName=log_group_name,
                startTime=int(start_time_ms),
                endTime=int(end_time_ms),
                filterPattern=filter_pattern,
                nextToken=next_token
            )
        else:
            response = client.filter_log_events(
                logGroupName=log_group_name,
                startTime=int(start_time_ms),
                endTime=int(end_time_ms),
                filterPattern=filter_pattern
            )

        all_events.extend(response['events'])

        next_token = response.get('nextToken')
        if not next_token:
            break

    return all_events



# Save logs to a single file ordered by logStreamName
def save_log_file(json_logs, file_path: str, file_name: str):
    
    # Ensure that logs contain the 'logStreamName' and 'timestamp' fields
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