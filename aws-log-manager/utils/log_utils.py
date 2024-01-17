from collections import defaultdict
from datetime import datetime
import json
import os
import re

# Save logs to a single file ordered by logStreamName
def save_to_file(logs, file_path, file_name):

    logs_by_stream_dict = get_logs_by_stream_name(logs)

    file_path = sanitize(os.path.join(file_path, f'{file_name}.json'))
    with open(file=file_path, mode='w') as file:
        for log_stream_name, logs in logs_by_stream_dict.items():
            for log in logs:
                file.write(json.dumps(log) + '\n')
    print(f"Logs saved to {file_path} in json format")

def get_logs_by_stream_name(logs):
    logs_by_stream_dict = defaultdict(list)
    for log in logs:
        log_stream_name = log['logStreamName']
        logs_by_stream_dict[log_stream_name].append(log)
    return logs_by_stream_dict

        
# Define a regex pattern to match only valid characters in file names or directories
def sanitize(filename):
    return re.sub(r'[^a-zA-Z0-9\_\-\.\\]', '_', filename).replace("LATEST", '')

# Define a function to print logs in an organized manner
def print_logs_to_console(logs):
   
   logs_by_stream_dict = get_logs_by_stream_name(logs)
   
   for log_stream_name, log_stream_items in logs_by_stream_dict.items():
    print("-" * 80)
    print(f"LogStreamName: {log_stream_name}")
    print("-" * 80)
    for item in log_stream_items:
        # Convert Unix timestamp to human-readable date and time
        log_datetime = datetime.fromtimestamp(item['timestamp'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
        print(f"Timestamp: {item['timestamp']}")
        print(f"DateTime: {log_datetime}")
        # print(f"IngestionTime: {item['ingestionTime']}")
        # print(f"EventId: {item['eventId']}")
        print(f"Message: {item['message']}")


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