from utils.log_utils import *
from utils.read_config import * 
import time
import boto3
import json

# Carregar o arquivo JSON
with open('aws-log-manager/config.json') as f:
    config_data = json.load(f)

FUNCTION_DICT = choose_function(config_data, pre_choice=None)

# Retrieve logs from AWS Lambda organized by logStreamName
client = boto3.client('logs')
log_group_name = f"/aws/lambda/{FUNCTION_DICT['functionName']}"

start_timestamp_ms = int(time.mktime(time.strptime(FUNCTION_DICT['startTime'], "%Y-%m-%dT%H:%M:%SZ"))) * 1000
end_timestamp_ms = int(time.mktime(time.strptime(FUNCTION_DICT['endTime'], "%Y-%m-%dT%H:%M:%SZ"))) * 1000

response = client.filter_log_events(
    logGroupName=log_group_name,
    startTime=start_timestamp_ms,
    endTime=end_timestamp_ms
)

logs = response['events']

if logs == None:
    raise ValueError("No log records were found!")

file_path = os.path.join(FUNCTION_DICT['baseFilePath'], f'logs_{FUNCTION_DICT['functionName']}_{FUNCTION_DICT['startTime']}.json')

save_to_file(logs, file_path)
