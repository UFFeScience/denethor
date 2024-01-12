from log_utils import *

# Define your start and end dates along with the Lambda function name
# start_time = "2023-11-27T14:25:00Z"
# end_time = "2023-12-31T23:59:59Z"
start_time = "2023-12-04T15:40:00Z"
end_time = "2023-12-31T23:59:59Z"
function_name = "tree_constructor"

file_path = "aws-log-manager/logs"

# Retrieve logs from AWS Lambda organized by logStreamName
def main():
    client = boto3.client('logs')
    log_group_name = f"/aws/lambda/{function_name}"

    start_timestamp = int(time.mktime(time.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")))
    end_timestamp = int(time.mktime(time.strptime(end_time, "%Y-%m-%dT%H:%M:%SZ")))

    response = client.filter_log_events(
        logGroupName=log_group_name,
        startTime=start_timestamp * 1000,  # in milliseconds
        endTime=end_timestamp * 1000  # in milliseconds
    )

    logs = response['events']
    logs_by_stream = defaultdict(list)

    for log in logs:
        log_stream_name = log['logStreamName']
        logs_by_stream[log_stream_name].append(log)


    file_prefix = "logs_"+ function_name
    save_logs_to_single_file(logs_by_stream, file_path, file_prefix)



if __name__ == "__main__":
    main()