from utils.log_utils import * 
import time
import boto3


# Define your start and end dates along with the Lambda function name
# start_time = '2024-01-18T14:44:00Z'
# end_time   = '2024-01-18T14:59:59Z'
# function_name = 'tree_constructor'
start_time = '2024-01-22T20:53:00Z'
end_time   = '2024-01-22T21:02:59Z'

function_name = 'tree_sub_find'
file_name = "logs_" + function_name

file_path = os.path.join('aws-log-manager', '_logs')

# Retrieve logs from AWS Lambda organized by logStreamName
def main():
    client = boto3.client('logs')
    log_group_name = f"/aws/lambda/{function_name}"

    start_timestamp_ms = int(time.mktime(time.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ"))) * 1000
    end_timestamp_ms = int(time.mktime(time.strptime(end_time, "%Y-%m-%dT%H:%M:%SZ"))) * 1000

    response = client.filter_log_events(
        logGroupName=log_group_name,
        startTime=start_timestamp_ms,
        endTime=end_timestamp_ms
    )

    logs = response['events']

    if logs == None:
        raise ValueError("No log records were found!")
    
    logs_sorted = sort_by_stream_and_timestamp(logs)
    
    save_to_file(logs_sorted, file_path, file_name)



if __name__ == "__main__":
    main()