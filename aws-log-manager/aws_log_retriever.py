from utils.log_utils import * 
import time
import boto3


# Define your start and end dates along with the Lambda function name
START_TIME = '2024-01-18T14:44:00Z'
END_TIME   = '2024-01-18T14:59:59Z'
FUNCTION_NAME = 'tree_constructor'
# START_TIME = '2024-01-22T20:53:00Z'
# END_TIME   = '2024-01-22T21:02:59Z'
# FUNCTION_NAME = 'tree_sub_find'

FILE_PATH = os.path.join('aws-log-manager', '_logs', f'logs_{FUNCTION_NAME}.json')

# Retrieve logs from AWS Lambda organized by logStreamName
def main():
    client = boto3.client('logs')
    log_group_name = f"/aws/lambda/{FUNCTION_NAME}"

    start_timestamp_ms = int(time.mktime(time.strptime(START_TIME, "%Y-%m-%dT%H:%M:%SZ"))) * 1000
    end_timestamp_ms = int(time.mktime(time.strptime(END_TIME, "%Y-%m-%dT%H:%M:%SZ"))) * 1000

    response = client.filter_log_events(
        logGroupName=log_group_name,
        startTime=start_timestamp_ms,
        endTime=end_timestamp_ms
    )

    logs = response['events']

    if logs == None:
        raise ValueError("No log records were found!")
    
    save_to_file(logs, FILE_PATH)

if __name__ == "__main__":
    main()