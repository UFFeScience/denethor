from utils.log_utils import *
from utils.read_config import * 
import time
import boto3
import json

# Carregar o arquivo JSON
with open('config/execution_config.json') as f:
    retriever_config = json.load(f)

function_data = choose_activity(retriever_config, pre_choice=1)

# Retrieve logs from AWS Lambda organized by logStreamName
client = boto3.client('logs')
log_group_name = f"/aws/lambda/{function_data['functionName']}"

start_timestamp_ms = int(time.mktime(time.strptime(function_data['startTime'], "%Y-%m-%dT%H:%M:%SZ"))) * 1000
end_timestamp_ms = int(time.mktime(time.strptime(function_data['endTime'], "%Y-%m-%dT%H:%M:%SZ"))) * 1000

response = client.filter_log_events(
    logGroupName=log_group_name,
    startTime=start_timestamp_ms,
    endTime=end_timestamp_ms
)

logs = response['events']

if logs == None:
    raise ValueError("No log records were found!")

file_path = function_data['baseFilePath'] 
file_name = f'logs_{function_data['functionName']}_{function_data['startTime']}.json'

save_to_file(logs, file_name, file_path)
