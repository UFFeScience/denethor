from collections import defaultdict
from datetime import datetime
import json
import time
import boto3
import re


# Function to retrieve AWS Lambda logs
def retrieve_lambda_logs(start_time, end_time, function_name):
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

    return logs_by_stream
    
    
    
# Function to filter AWS Lambda logs by keywords
def filter_logs_by_keywords(logs_by_stream, keywords):
    
    filtered_logs_by_stream = defaultdict(list)

    for log_stream_name, logs in logs_by_stream.items():
        for log in logs:
            message = log.get('message')

            if message:
                encoded_message = message.encode('utf-8', 'ignore').decode('utf-8')

                for keyword in keywords:
                    if keyword.encode('utf-8', 'ignore').decode('utf-8') in encoded_message:
                        filtered_logs_by_stream[log_stream_name].append(log)
                        break

    return filtered_logs_by_stream


# Save logs to a single file ordered by logStreamName
def save_logs_to_single_file(logs_by_stream, file_prefix):
    file_path = f"{file_prefix}.json"
    file_path = sanitize_filename(file_path)
    with open(file_path, 'w') as file:
        for log_stream_name, logs in logs_by_stream.items():
            for log in logs:
                file.write(json.dumps(log) + '\n')
    print(f"Logs saved to {file_path} in json format")

        
# Save logs to multiple files ordered and grouped by logStreamName
def save_logs_to_multiple_files(logs_by_stream, file_prefix):
    for log_stream_name, logs in logs_by_stream.items():
        file_path = f"{file_prefix}_{log_stream_name}.json"
        file_path = sanitize_filename(file_path)

        with open(file_path, 'w') as file:
            for log in logs:
                file.write(json.dumps(log) + '\n')
        print(f"Logs saved to {file_path} in json format")



# Define a regex pattern to match only valid characters in file names
def sanitize_filename(filename):
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', filename).replace("LATEST", '')

# Define a function to print logs in an organized manner
def print_logs_to_console(log_stream_dict):
   for log_stream_name, log_stream_items in log_stream_dict.items():
    print("-" * 80)
    print(f"Log Stream Name: {log_stream_name}")
    print("-" * 80)
    for item in log_stream_items:
        # Convert Unix timestamp to human-readable date and time
        log_datetime = datetime.fromtimestamp(item['timestamp'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
        print(f"Timestamp: {item['timestamp']}")
        print(f"DateTime: {log_datetime}")
        # print(f"IngestionTime: {item['ingestionTime']}")
        # print(f"EventId: {item['eventId']}")
        print(f"Message: {item['message']}")

        

# # Define a function to save logs with readable timestamps to a file
# def save_logs_to_file_custom(logs, file_path):
#     with open(file_path, 'w') as file:
#         for log in logs:
#             # Convert Unix timestamp to human-readable date and time
#             log_datetime = datetime.fromtimestamp(log["timestamp"] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')

#             file.write("LogStreamName: " + log["logStreamName"] + "\n")
#             file.write("Timestamp:" + str(log["timestamp"]) + "\n")
#             file.write("DateTime:" + log_datetime + "\n")
#             file.write("Message: " + log["message"])# + "\n")
#             file.write("IngestionTime: " + str(log["ingestionTime"]) + "\n")
#             file.write("EventId: " + log["eventId"] + "\n")
#             file.write("-" * 80 + "\n")  # Separator for better readability

#     print(f"Logs saved to {file_path}")
