from datetime import datetime, timezone
import json
import os
import re

# Sort the list by the logStreamName attribute and then by the timestamp attribute
def sort_by_stream_and_timestamp(logs):
    return sorted(logs, key=lambda x: (x["logStreamName"], x["timestamp"]))

        
# Define a regex pattern to match only valid characters in file names or directories
def sanitize(filename):
    return re.sub(r'[^a-zA-Z0-9\_\-\.\\]', '_', filename).replace("LATEST", '')

# Save logs to a single file ordered by logStreamName
def save_to_file(logs, file_path, file_name):
    file_path = sanitize(os.path.join(file_path, f'{file_name}.json'))
    with open(file=file_path, mode='w') as file:
        file.write('[\n')
        for i, log in enumerate(logs):
            last = i == len(logs) - 1
            file.write('\t' + json.dumps(log) + ('\n' if last else ',\n'))
        file.write(']\n')
    print(f"Logs saved to {file_path} in json format")

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


# Function to filter AWS Lambda logs by keywords
def filter_logs_by_keywords(logs, keywords):
    filtered_logs = []
    for log in logs:
        message = log.get('message')
        if message:
            encoded_message = message.encode('utf-8', 'ignore').decode('utf-8')
            for keyword in keywords:
                if keyword.encode('utf-8', 'ignore').decode('utf-8') in encoded_message:
                    filtered_logs.append(log)
                    break
    return filtered_logs


# Create datetime objects (in UTC) from the timestamps in milliseconds
def convert_to_datetime(time: float):
    if time:
        return datetime.fromtimestamp((time / 1000.0), tz=timezone.utc)
    return None

def clear (dicio):
    for chave in dicio:
        dicio[chave] = None
    return dicio