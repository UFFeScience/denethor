import boto3
import os
import time
import json

# realiza o upload de arquivos para um bucket S3 / AWS
def upload_files_to_s3(params):
    s3 = boto3.client('s3')
    bucket = params['bucket']
    key = params['key']
    files = params['files']
    path = params['path']
    for file_name in files:
        # Caminho completo para o arquivo
        file_path = os.path.join(path, file_name)
        file_key = os.path.join(key, file_name)
        # Fazer o upload do arquivo para o S3
        s3.upload_file(file_path, bucket, file_key)
        print(f'File {file_key} uploaded to {bucket}')



def download_files_from_s3(params):
    s3 = boto3.client('s3')
    bucket = params['bucket']
    key = params['key']
    files = params['files']
    downloadPath = params['downloadPath']
    downloadPath.replace('[executionId]', params['executionId'])
    for file_name in files:
        # Caminho completo para o arquivo
        file_path = os.path.join(downloadPath, file_name)
        file_key = os.path.join(key, file_name)
        # Fazer o download do arquivo do S3
        s3.download_file(bucket, file_key, file_path)
        print(f'File {file_key} downloaded from {bucket}')



def trigger_lambda_execution(params):
    base_payload = {
        'inputBucket': params['inputBucket'],
        'inputKey': params['inputKey'],
        'outputBucket': params['outputBucket'],
        'outputKey': params['outputKey']
    }

    files = params['files']
    execution_strategy = params['execution_strategy']
    lambda_function = params['lambdaFunction']
    
    requests = []

    if execution_strategy == 'for_each_file':
        for file_name in files:
            payload = base_payload | {'file': file_name}
            request_id = invoke_async(lambda_function, payload)
            requests.append(request_id)

    elif execution_strategy == 'for_all_files':
        payload = base_payload | {'files': files}
        request_id = invoke_async(lambda_function, payload)
        requests.append(request_id)
    
    else:
        raise ValueError(f'Invalid execution strategy: {execution_strategy}')
    
    print(f'{lambda_function} triggered with payload {base_payload} with execution strategy {execution_strategy} for files: {files}')
    return requests

def invoke_async(lambda_function, payload):
    lambda_client = boto3.client('lambda')
    response = lambda_client.invoke(
                FunctionName=lambda_function,
                InvocationType='Event',
                Payload=json.dumps(payload)
            )
    request_id = response['ResponseMetadata']['RequestId']
    return request_id




def wait_for_lambda_completion(function_name, requests):
    lambda_client = boto3.client('lambda')
    completed_requests = {}  # Dicionário para armazenar o estado dos requests

    while len(completed_requests) != len(requests):
        time.sleep(5)

        for request_id in requests:
            if request_id in completed_requests:
                continue  # Skip already completed requests
            
            response = lambda_client.get_function_execution(
                FunctionName=function_name,
                Qualifier=request_id
            )
            status = response['Status']
            
            if status == 'RUNNING':
                print(f'Lambda function {function_name} with request ID {request_id} is still running.')
            elif status == 'SUCCESS':
                print(f'Lambda function {function_name} with request ID {request_id} has completed successfully')
                completed_requests[request_id] = 'SUCCESS'  # request completed successfully
            elif status == 'FAILED':
                print(f'Lambda function {function_name} with request ID {request_id} has failed')
                completed_requests[request_id] = 'FAILED'  # request completed with error
            else:
                print(f'Lambda function {function_name} with request ID {request_id} has an unknown status: {status}')
        