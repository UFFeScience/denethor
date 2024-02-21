from utils.log_utils import *
import time
import boto3
import json

def retrive_log():
    # Carregar o arquivo JSON
    with open('config/execution_info.json') as f:
        EXECUTION_INFO = json.load(f)

    # Retrieve logs from AWS Lambda organized by logStreamName
    client = boto3.client('logs')
    log_group_name = f"/aws/lambda/{EXECUTION_INFO['activityName']}"

    start_timestamp_ms = int(time.mktime(time.strptime(EXECUTION_INFO['startTime'], "%Y-%m-%dT%H:%M:%SZ"))) * 1000
    end_timestamp_ms = int(time.mktime(time.strptime(EXECUTION_INFO['endTime'], "%Y-%m-%dT%H:%M:%SZ"))) * 1000

    response = client.filter_log_events(
        logGroupName=log_group_name,
        startTime=start_timestamp_ms,
        endTime=end_timestamp_ms
    )

    logs = response['events']

    if logs == None:
        raise ValueError("No log records were found!")

    # file_name = f'logs_{function_data['functionName']}_{function_data['startTime']}.json'

    save_to_file(logs, EXECUTION_INFO['logFile'])
