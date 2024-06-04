import boto3
import logging
import timeit
import os
import re

#
## LIMPEZA ##
#
def remove_files(dir_path: str) -> None:
    if os.path.exists(dir_path):
        # Walk through all files and directories within dir_path
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f'Removed the file {file_path}')
    else:
        print(f'Sorry, directory {dir_path} did not exist.')


def create_directory_if_not_exists(*dir_paths) -> None:
    for dir in dir_paths:
        if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True) # cria o diretório, caso não exista
            print(f'Directory {dir} was created!')


def directory_has_single_file(dir_path: str) -> bool:
    if not os.path.isdir(dir_path):
        return False
    files = os.listdir(dir_path)
    if len(files) != 1:
        return False
    return True


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


def upload_to_s3(request_id: str, s3_bucket: str, s3_key: str, file_list: list, local_path: str) -> int:
    total_upload_duration_ms = 0
    
    for file_name in file_list:
        # upload files from lambda function into s3
        duration_ms = upload_file_to_s3(request_id, s3_bucket, s3_key, file_name, local_path)
        
        total_upload_duration_ms += duration_ms
    
    return total_upload_duration_ms



def download_file_from_s3(request_id: str, s3_bucket: str, s3_key: str, file_name: str, local_path: str) -> int:
    
    start_time = timeit.default_timer()
    
    validade_required_params(request_id, s3_bucket, file_name, local_path)

    s3 = boto3.client('s3')

    # verificando se o nome do arquivo já está presente na s3_key
    # dependendo da forma que a requisição é feita, o nome do arquivo ppode já estar incluso na s3_key
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


def download_from_s3(request_id: str, s3_bucket: str, s3_key: str, file_list: list, local_path: str) -> int:
    total_download_duration_ms = 0
    
    for file_name in file_list:
        # download files from s3 into lambda function
        duration_ms = download_file_from_s3(request_id, s3_bucket, s3_key, file_name, local_path)
        
        total_download_duration_ms += duration_ms
    
    return total_download_duration_ms
