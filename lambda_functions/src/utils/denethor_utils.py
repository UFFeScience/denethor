from datetime import datetime
import json
import os
import platform
import uuid
import utils.file_utils as fu
import utils.logger as dl

LOCAL_WIN = 'local_win'
AWS_LAMBDA = 'aws_lambda'
VM_LINUX = 'vm_linux'

def generate_uuid():
    return 'uuid_' + str(uuid.uuid4()).replace('-', '_')

def get_request_id(context):
    return context.aws_request_id if context else generate_uuid()

def get_execution_env(event):
    return event.get('execution_env')

def handle_consumed_files(request_id: str, files: list, file_path: str, params: dict):
    
    download_time_ms = None
    if params.get('execution_env').get('env_name') == AWS_LAMBDA:
        # Get the input_bucket from the payload
        bucket = params.get('input_bucket')
        key = params.get('input_key')
        # Download file from s3 bucket into lambda function
        download_time_ms = fu.download_from_s3(request_id, bucket, key, files, file_path)
        
    info = fu.get_files_info(files, file_path)      
    print(f'CONSUMED_FILES_INFO RequestId: {request_id}\t FilesCount: {info['files_count']} files\t FilesSize: {info['files_size']} bytes\t TransferDuration: {download_time_ms} ms\t ConsumedFiles: {files}')


def handle_produced_files(request_id: str, files: list, files_path: str, params: dict):

    upload_duration_ms = None
    if params.get('execution_env').get('env_name') == AWS_LAMBDA:
        ## Copy tree file to S3 ##
        bucket = params.get('output_bucket')
        key = params.get('output_key')
        
        # Upload files from lambda function into s3
        upload_duration_ms = fu.upload_to_s3(request_id, bucket, key, files, files_path)
    
    info = fu.get_files_info(files, files_path)      
    print(f'PRODUCED_FILES_INFO RequestId: {request_id}\t FilesCount: {info['files_count']} files\t FilesSize: {info['files_size']} bytes\t TransferDuration: {upload_duration_ms} ms\t ProducedFiles: {files}')
        



def print_env(execution_env):
    print(f'============== Ambiente de execução: {execution_env.get('env_name')} ==============')
    print(f'Start time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('pwd:', os.getcwd())
    for label, value in execution_env.items():
        print(f'{label}={value}')
        # print(os.listdir(value) if 'PATH' in label else '')  
    print('===========================================================')

def print_env_to_log(execution_env, logger):
    logger.info(f'============== Ambiente de execução: {execution_env.get('env_name')} ==============')
    logger.info(f'Start time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    logger.info('pwd:', os.getcwd())
    for label, value in execution_env.items():
        logger.info(f'{label}={value}')
        # logger.info(os.listdir(value) if 'PATH' in label else '')  
    logger.info('===========================================================')

