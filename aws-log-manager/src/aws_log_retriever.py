from utils.log_utils import *
import time
import boto3
import json

def retrieve_logs_from_aws(params):

    # Retrieve logs from AWS Lambda organized by logStreamName
    client = boto3.client('logs')
    
    execution_id = params['executionId']
    start_timestamp_ms = params['workflowStartTimeMs']
    end_timestamp_ms = int(time.time() * 1000) #timesstamp atual
    
    lambda_functions = params['lambdaFunctions']
    log_path = params['logPath']
    log_file = params['logFile']
    
    file_path = log_path.replace('[executionId]', execution_id)

    for function_name in lambda_functions:
        log_group_name = f"/aws/lambda/{function_name}"
        response = client.filter_log_events(
            logGroupName=log_group_name,
            startTime=start_timestamp_ms,
            endTime=end_timestamp_ms
        )
        logs = response['events']
        if logs == None:
            raise ValueError("No log records were found!")
        
        file_name = log_file.replace('[lambdaFunction]', function_name).replace('[executionId]', execution_id)
        
        save_to_file(logs, file_path, file_name)
