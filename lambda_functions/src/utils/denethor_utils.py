from datetime import datetime
import json
import os
import platform
import file_utils as fu

LOCAL_WIN = 'LOCAL_WIN'
LAMBDA = 'LAMBDA'
VM_LINUX = 'VM_LINUX'

def get_request_id(event, context):
    if context is None:
        request_id = event.get('request_id', '0')
    else:
        request_id = context.aws_request_id
    return request_id

def handle_consumed_files(request_id: str, file: str, file_path: str, params: dict):
    env_config = params.get('env_config')
    env_name = params.get('env_name')
    
    download_time_ms = None
    if env_name == LAMBDA:
        # Get the input_bucket from the payload
        bucket = params.get('inputBucket')
        key = params.get('inputKey')
        # Download file from s3 bucket into lambda function
        download_time_ms = fu.download_file_from_s3(request_id, bucket, key, file, file_path)
        
    info = fu.get_files_info(file, file_path)      
    print(f'CONSUMED_FILES_INFO RequestId: {request_id}\t FilesCount: {info['files_count']} files\t FilesSize: {info['files_size']} bytes\t TransferDuration: {download_time_ms} ms\t ConsumedFiles: {input_file}')


def handle_produced_files(request_id: str, files: list, files_path: str, params: dict):
    env_config = params.get('env_config')
    env_name = params.get('env_name')

    upload_duration_ms = None
    if env_name == LAMBDA:
        ## Copy tree file to S3 ##
        bucket = params.get('outputBucket')
        key = params.get('outputKey')
        
        # Upload files from lambda function into s3
        upload_duration_ms = fu.upload_to_s3(request_id, bucket, key, files, files_path)
    
    info = fu.get_files_info(files, files_path)      
    print(f'PRODUCED_FILES_INFO RequestId: {request_id}\t FilesCount: {info['files_count']} files\t FilesSize: {info['files_size']} bytes\t TransferDuration: {upload_duration_ms} ms\t ProducedFiles: {files}')
        


def print_path(label, path):
    if os.path.exists(path):
        print(f'{label}={path}:', os.listdir(path))
    else:
        print(f'{label} does not exist')

def print_env(env_name, env_conf):
    print(f'============== Ambiente de execução: {env_name} ==============')
    print(f'Start time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('pwd:', os.getcwd())
    for key, value in env_conf.items():
        print_path(label=key, path=value)
    
    print('===========================================================')

