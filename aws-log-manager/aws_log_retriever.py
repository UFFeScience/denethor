from utils.log_utils import *
from utils.read_config import * 
import time
import boto3
import json

CONFIG = choose_function()

# Retrieve logs from AWS Lambda organized by logStreamName
client = boto3.client('logs')
log_group_name = f"/aws/lambda/{CONFIG['function_name']}"

start_timestamp_ms = int(time.mktime(time.strptime(CONFIG['start_time'], "%Y-%m-%dT%H:%M:%SZ"))) * 1000
end_timestamp_ms = int(time.mktime(time.strptime(CONFIG['end_time'], "%Y-%m-%dT%H:%M:%SZ"))) * 1000

response = client.filter_log_events(
    logGroupName=log_group_name,
    startTime=start_timestamp_ms,
    endTime=end_timestamp_ms
)

logs = response['events']

if logs == None:
    raise ValueError("No log records were found!")

file_path = os.path.join(CONFIG['base_file_path'], f'logs_{CONFIG['function_name']}_{CONFIG['start_time']}.json')
save_to_file(logs, file_path)
