from datetime import datetime, timezone
import json
import os
import re

# Define a regex pattern to match only valid characters in file names or directories
def sanitize(filename):
    return re.sub(r'[^a-zA-Z0-9\_\-\.\\]', '_', filename).replace("LATEST", '')


# Save logs to a single file ordered by logStreamName
def save_to_file(json_logs, file_name, file_path):
    
    json_logs.sort(key=lambda x: (x['logStreamName'], x['timestamp']))
    
    file_name_with_path = os.path.join(file_path, sanitize(file_name))
    with open(file=file_name_with_path, mode='w') as file:
        json.dump(json_logs, file, indent=2)
    
    print(f"Logs saved to {file_name} in json format")


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


# Create datetime objects (in UTC) from the timestamps in milliseconds
def to_datetime(time: float):
    if time:
        return datetime.fromtimestamp((time / 1000.0), tz=timezone.utc)
    return None

def parse_int(value: str) -> int:
    # value_int = value.replace('bytes', '').replace('MB', '').replace('files', '').strip() if value else None
    # return int(value_int) if value_int else None
    match = re.search(r"\d+", value)
    value_int = int(match.group()) if match else None
    return value_int

def parse_float(value: str) -> float:
    # value_float = value.replace('ms', '').strip() if value else None
    # return float(value_float) if value_float else None
    match = re.search(r"\d+\.?\d*", value)
    value_float = float(match.group()) if match else None
    return value_float


# Agrupando logs pelo valor de 'RequestId' no campo 'message' 
def get_logs_by_request_id(logs: dict) -> dict:
    
    # Dicionário para armazenar os logs filtrados
    request_id_dict = {}
   
    # Loop através dos logs
    for log in logs:
        # Obter o RequestId do log
        request_id = get_request_id(log['message'])
        
        # Se o RequestId não for None, adicione o log ao dicionário
        if request_id is not None:
            if request_id not in request_id_dict:
                request_id_dict[request_id] = []
            request_id_dict[request_id].append(log)

    return request_id_dict


def get_request_id(log_message):
    match = re.search('RequestId: (\\S+)', log_message)
    request_id = match.group(1) if match else None
    return request_id
