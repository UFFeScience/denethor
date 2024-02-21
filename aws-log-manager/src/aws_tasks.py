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
        print(f'aws_tasks.upload_files_to_s3 -> File {file_key} uploaded to {bucket}')


def download_file_from_s3(bucket, dataFiles):
    s3 = boto3.client('s3')


def trigger_lambda_execution(params):
    
    lambda_client = boto3.client('lambda')

    base_payload = {
        'inputBucket': params['inputBucket'],
        'inputKey': params['inputKey'],
        'outputBucket': params['outputBucket'],
        'outputKey': params['outputKey'],
    }

    files = params['files']
    execution_strategy = params['execution_strategy']
    lambda_function = params['lambdaFunction']
    
    if execution_strategy == 'for_each_file':
        for file_name in files:
            
            payload = base_payload | {'file': file_name}
            
            response = lambda_client.invoke(
                FunctionName=lambda_function,
                InvocationType='Event',
                Payload=json.dumps(payload)
            )
            print(f'aws_tasks.trigger_lambda_execution -> Lambda function {lambda_function} triggered with payload {payload} execution_strategy {execution_strategy}')
    
    elif execution_strategy == 'for_all_files':
        
        payload = base_payload | {'files': files}
        
        response = lambda_client.invoke(
            FunctionName=lambda_function,
            InvocationType='Event',
            Payload=json.dumps(payload)
        )
        print(f'aws_tasks.trigger_lambda_execution -> Lambda function {lambda_function} triggered with payload {payload} execution_strategy {execution_strategy}')
    
    else:
        raise ValueError(f'Invalid execution strategy: {execution_strategy}')
    
    return response

def wait_for_lambda_completion(function_name):
    lambda_client = boto3.client('lambda')
    # while True:
    #     response = lambda_client.get_function(
    #         FunctionName=function_name
    #     )
    #     if response['Configuration']['State'] == 'Active':
    #         break
    #     time.sleep(5)