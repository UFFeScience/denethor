from utils.log_utils import *
import time
import boto3
import json


def retrieve_logs_from_aws(params):

    # Retrieve logs from AWS Lambda organized by logStreamName
    client = boto3.client('logs')
    
    execution_id = params['executionId']
    start_timestamp_ms = params['workflowStartTimeMs']
    # Se não houver o parâmetro endTimeLogRetriever, então o valor padrão é o timestamp atual
    end_timestamp_ms = params.get('endTimeLogRetriever', int(time.time() * 1000))
    
    functions = params['functions']
    log_path = params['logPath']
    log_file = params['logFile']
    
    file_path = log_path.replace('[executionId]', execution_id)

    for function_name in functions:
        log_group_name = f"/aws/lambda/{function_name}"
        response = client.filter_log_events(
            logGroupName=log_group_name,
            startTime=start_timestamp_ms,
            endTime=end_timestamp_ms
        )
        logs = response['events']
        if logs == None or len(logs) == 0:
            raise ValueError("No log records were found!")
        
        file_name = log_file.replace('[functionName]', function_name).replace('[executionId]', execution_id)
        
        save_to_file(logs, file_path, file_name)

        print(f"Logs saved to {file_path}/{file_name} in json format")


# PARA TESTAR LOCALMENTE!!!!

# Carregar o workflow do arquivo JSON
# with open('config/workflow_model.json', 'r') as f:
#     workflow_model = json.load(f)

    
# #tree_constructor: 1707761189949 / subtree_mining: 1707955643601
# workflow_start_time_ms = 1707761189949 
# workflow_start_time_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(workflow_start_time_ms/1000))

# execution_id = 'EXEC_' + workflow_start_time_str.replace(':', '-').replace('T', '_').replace('Z', '') + '_UTC'

# end_time_log_retriever = 1707955643601 + (15*60*1000) # 15 min
# execution_params = {
#     "executionId": execution_id,
#     "workflowStartTimeStr": workflow_start_time_str,
#     "workflowStartTimeMs": workflow_start_time_ms,
#     "dataFiles": workflow_model['workflow']['dataFiles'],
#     "endTimeLogRetriever": end_time_log_retriever
# }

# params = {}
# for step in workflow_model['workflow']['steps']:
#     if step['handler'] == 'retrieve_logs_from_aws':
#         params =  step['params']
#         break

# retrieve_logs_from_aws(execution_params | params)