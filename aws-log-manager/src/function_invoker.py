import boto3
import os
import time
import json

def invoke_lambda_execution(params):
    base_payload = {
        'inputBucket': params['inputBucket'],
        'inputKey': params['inputKey'],
        'outputBucket': params['outputBucket'],
        'outputKey': params['outputKey']
    }

    files = params['dataFiles']['files']
    execution_strategy = params['execution_strategy']
    function_name = params['functionName']
    
    requests = []

    if execution_strategy == 'for_each_file':
        for file_name in files:
            payload = base_payload | {'file': file_name}
            request_id = invoke_async(function_name, payload)
            requests.append(request_id)

    elif execution_strategy == 'for_all_files':
        payload = base_payload | {'files': files}
        request_id = invoke_async(function_name, payload)
        requests.append(request_id)
    
    else:
        raise ValueError(f'Invalid execution strategy: {execution_strategy}')
    
    print(f'{function_name} triggered with payload {base_payload} with execution strategy {execution_strategy} for files: {files}')
    return {f"{function_name}_requests" : requests}


def invoke_async(function_name, payload):
    lambda_client = boto3.client('lambda')
    response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='Event',
                Payload=json.dumps(payload)
            )
    request_id = response['ResponseMetadata']['RequestId']
    return request_id