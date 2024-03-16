from datetime import datetime
import json
import os
import re
from utils import utils

# Save logs to a single file ordered by logStreamName
def save_to_file(json_logs, file_path, file_name):
    # garantir que os logs contenham o campo 'logStreamName' e 'timestamp'
    if not all('logStreamName' in log and 'timestamp' in log for log in json_logs):
        raise ValueError("Logs must contain 'logStreamName' and 'timestamp' fields")
    json_logs.sort(key=lambda x: (x['logStreamName'], x['timestamp']))
    
    # Sanitize file name
    file_name = utils.sanitize(file_name)

    # Create the directory if it does not exist
    os.makedirs(file_path, exist_ok=True)

    file = os.path.join(file_path, file_name)
    with open(file=file, mode='w') as file:
        json.dump(json_logs, file, indent=2)
    
    print(f"Logs saved to {file} in json format")


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


# Agrupando logs pelo valor de 'RequestId' no campo 'message' 
def group_logs_by_request(logs: dict) -> dict:
    
    # Dicionário para armazenar os logs filtrados
    logs_by_request = {}
   
    # Loop através dos logs
    for log in logs:
        # Obter o RequestId do log
        request_id = get_request_id(log['message'])
        
        # Se o RequestId não for None, adicione o log ao dicionário
        if request_id is not None:
            if request_id not in logs_by_request:
                logs_by_request[request_id] = []
            logs_by_request[request_id].append(log)

    return logs_by_request


def get_request_id(log_message):
    match = re.search('RequestId: (\\S+)', log_message)
    request_id = match.group(1) if match else None
    return request_id
