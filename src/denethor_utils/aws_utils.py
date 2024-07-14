import os
import boto3
import timeit
import logging
from src.constants import LOCAL, AWS_LAMBDA, VM_LINUX


##
# Consumed (download) Files
##
def handle_consumed_files(request_id: str, files_name: list, path: str, params: dict):
    download_time_ms = None
    if params.get('env_name') == AWS_LAMBDA:
        # Get the bucket from the payload
        bucket = params.get('input_bucket')
        key = params.get('input_key')
        # Download file from s3 bucket into lambda function
        download_time_ms = download_from_s3(request_id, bucket, key, files_name, path)
        
    info = get_files_info(files_name, path)      
    print(f'CONSUMED_FILES_INFO RequestId: {request_id}\t FilesCount: {info['files_count']} files\t FilesSize: {info['files_size']} bytes\t TransferDuration: {download_time_ms} ms\t ConsumedFiles: {files_name}')

def download_from_s3(request_id: str, s3_bucket: str, s3_key: str, files_name: list, local_path: str) -> int:
    total_download_duration_ms = 0
    for file_name in files_name:
        # download files from s3 into lambda function
        duration_ms = download_file_from_s3(request_id, s3_bucket, s3_key, file_name, local_path)
        total_download_duration_ms += duration_ms
    return total_download_duration_ms

def download_file_from_s3(request_id: str, s3_bucket: str, s3_key: str, file_name: str, local_path: str) -> int:
    start_time = timeit.default_timer()
    validade_required_params(request_id, s3_bucket, file_name, local_path)

    s3 = boto3.client('s3')

    # verificando se o nome do arquivo já está presente na s3_key
    # dependendo da forma que a requisição é feita, o nome do arquivo pode já estar incluso na s3_key
    if not s3_key.endswith(file_name):
        s3_key = os.path.join(s3_key, file_name)

    # file_name = os.path.basename(s3_key) # basename representa o nome do arquivo
    local_file_path = os.path.join(local_path, file_name)

    s3.download_file(s3_bucket, s3_key, local_file_path)
    
    end_time = timeit.default_timer()
    download_time_ms = (end_time - start_time) * 1000
    file_size = os.stat(local_file_path).st_size

    print(f'Download Successful from S3! File {file_name} | {file_size} bytes | {download_time_ms} milissegundos')
    print(f'FILE_TRANSFER RequestId: {request_id}\t TransferType: consumed\t FileName: {file_name}\t Bucket: {s3_bucket}\t FilePath: {s3_key}\t LocalFilePath: {local_file_path}\t TransferDuration: {download_time_ms} ms\t FileSize: {file_size} bytes')

    return download_time_ms
      



##
# Produced (upload) Files
##
def handle_produced_files(request_id: str, files_name: list, files_path: str, params: dict):
    upload_duration_ms = None
    if params.get('env_name') == AWS_LAMBDA:
        bucket = params.get('output_bucket')
        key = params.get('output_key')
        # Upload files from lambda function into s3
        upload_duration_ms = upload_to_s3(request_id, bucket, key, files_name, files_path)
    info = get_files_info(files_name, files_path)      
    print(f'PRODUCED_FILES_INFO RequestId: {request_id}\t FilesCount: {info['files_count']} files\t FilesSize: {info['files_size']} bytes\t TransferDuration: {upload_duration_ms} ms\t ProducedFiles: {files_name}')
  

def upload_to_s3(request_id: str, s3_bucket: str, s3_key: str, file_list: list, local_path: str) -> int:
    total_upload_duration_ms = 0
    for file_name in file_list:
        # upload files from lambda function into s3
        duration_ms = upload_file_to_s3(request_id, s3_bucket, s3_key, file_name, local_path)
        total_upload_duration_ms += duration_ms
    return total_upload_duration_ms

def upload_file_to_s3(request_id: str, s3_bucket: str, s3_key: str, file_name: str, local_path: str) -> int:
    upload_duration_ms = 0
    try:
        start_time = timeit.default_timer()
        validade_required_params(request_id, s3_bucket, file_name, local_path)
        
        s3 = boto3.client('s3')
        s3_key_upload = os.path.join(s3_key, file_name)
        local_file = os.path.join(local_path, file_name)

        s3.upload_file(local_file, s3_bucket, s3_key_upload)

        end_time = timeit.default_timer()
        upload_duration_ms = (end_time - start_time) * 1000
        file_size = os.stat(local_file).st_size
        
        print(f'Upload Successful to S3! File {file_name} | {file_size} bytes | {upload_duration_ms} milissegundos')
        print(f'FILE_TRANSFER RequestId: {request_id}\t TransferType: produced\t FileName: {file_name}\t Bucket: {s3_bucket}\t FilePath: {s3_key_upload}\t LocalFilePath: {local_file}\t TransferDuration: {upload_duration_ms} ms\t FileSize: {file_size} bytes')

    except FileNotFoundError as e:
        print(f'The local file {local_file} was not found!')
        logging.error(e)
        raise e
    
    return upload_duration_ms




##
# Auxiliar and Validation Functions
##
def get_files_info(files: list, path: str) -> dict:
    files_name = []
    files_count = 0
    files_size = 0
    for file in os.listdir(path):
        fp = os.path.join(path, file)
        if os.path.isfile(fp) and (files is None or file in files):
            files_count += 1
            files_size += os.path.getsize(fp)
            files_name.append(file)
    return {'files_name': files_name, 'files_count': files_count, 'files_size': files_size}


def validade_required_params(request_id: str, s3_bucket: str, file_name: str, local_path: str) -> None:
    if request_id is None:
        raise ValueError('request_id cannot be None when downloading/uploading from S3!')
    
    if s3_bucket is None:
        raise ValueError('s3_bucket cannot be None when downloading/uploading from S3!')
    
    if file_name is None:
        raise ValueError('file_name cannot be None when downloading/uploading from S3!')
    
    if local_path is None:
        raise ValueError('local_path cannot be None when downloading/uploading from S3!')
    
    if not os.path.exists(local_path):
        raise ValueError('local_path does not exist!')














# def upload_files_to_aws_s3(params):
#     """
#     Uploads files to an AWS S3 bucket.

#     Args:
#         params (dict): A dictionary containing the following keys:
#             - bucket (str): The name of the S3 bucket.
#             - key (str): The key prefix for the uploaded files.
#             - dataFiles (dict): A dictionary containing the following keys:
#                 - files (list): A list of file names to be uploaded.
#                 - path (str): The path to the directory containing the files.

#     Returns:
#         None
#     """
#     s3 = boto3.client('s3')
#     bucket = params['bucket']
#     key = params['key']
#     files = params['input_files_name']
#     path = params['input_files_path']
#     for file_name in files:
#         # Full path to the file
#         file_path = os.path.join(path, file_name)
#         file_key = os.path.join(key, file_name)
#         # Upload the file to S3
#         s3.upload_file(file_path, bucket, file_key)
#         print(f'File {file_key} uploaded to {bucket}')


# def download_files_from_aws_s3(params):
#     """
#     Downloads files from an S3 bucket to a specified local directory.

#     Args:
#         params (dict): A dictionary containing the following parameters:
#             - bucket (str): The name of the S3 bucket.
#             - key (str): The key prefix for the files in the S3 bucket.
#             - dataFiles (dict): A dictionary containing the list of files to download.
#                 - files (list): A list of file names to download.
#             - downloadPath (str): The local directory path where the files will be downloaded.
#             - execution_id (str): An execution ID used to replace a placeholder in the download path.

#     Returns:
#         None

#     Raises:
#         botocore.exceptions.NoCredentialsError: If AWS credentials are not found.
#         botocore.exceptions.ParamValidationError: If the input parameters are invalid.
#         botocore.exceptions.EndpointConnectionError: If there is an error connecting to the S3 endpoint.
#         botocore.exceptions.ClientError: If there is an error downloading the file from S3.

#     """
#     s3 = boto3.client('s3')
#     bucket = params['bucket']
#     key = params['key']
#     files = params['files']
#     downloadPath = params['downloadPath']
#     downloadPath.replace('[execution_id]', params['execution_id'])
#     for file_name in files:
#         # Full path to the file
#         file_path = os.path.join(downloadPath, file_name)
#         file_key = os.path.join(key, file_name)
#         # Download the file from S3
#         s3.download_file(bucket, file_key, file_path)
#         print(f'File {file_key} downloaded from {bucket}')
