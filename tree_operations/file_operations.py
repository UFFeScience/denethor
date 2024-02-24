import os
import logging
import boto3
import timeit

#
# ## LIMPEZA ##
#
# remove files from a path
def remove_files(dir_path):
    if os.path.exists(dir_path):
        #lista somente os arquivos dentro do diretório
        files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        for name_file in files:
            file_path = os.path.join(dir_path, name_file)
            os.remove(file_path)
            print(f'Removed the file {file_path}')     
    else:
        print(f'Sorry, directory {dir_path} did not exist.')
        os.makedirs(dir_path, exist_ok=True) # cria o diretório, caso não exista
        print(f'Directory {dir_path} was created!')


def directory_has_single_file(directory_path):
    if not os.path.isdir(directory_path):
        return False
    files = os.listdir(directory_path)
    if len(files) != 1:
        return False
    return True


def get_num_files_and_size(path):
    num_files = 0
    total_size = 0
    for file in os.listdir(path):
        fp = os.path.join(path, file)
        if os.path.isfile(fp):
            num_files += 1
            total_size += os.path.getsize(fp)
    
    return num_files, total_size


def upload_and_log_to_s3(request_id, s3_bucket, s3_key, file_name, local_path):
    s3 = boto3.client('s3')
    s3_key_upload = os.path.join(s3_key, file_name)
    local_file_path = os.path.join(local_path, file_name)

    try:
        start_time = timeit.default_timer()
        s3.upload_file(local_file_path, s3_bucket, s3_key_upload)
        end_time = timeit.default_timer()
        upload_time_ms = (end_time - start_time) * 1000
        file_size = os.stat(local_file_path).st_size

        print(f'Upload Successful to S3! File {file_name} | {file_size} bytes | {upload_time_ms} milissegundos')
    
        print(f'FILE_TRANSFER RequestId: {request_id}\t TransferType: produced\t FileName: {file_name}\t Bucket: {s3_bucket}\t FilePath: {s3_key_upload}\t LocalFilePath: {local_file_path}\t TransferDuration: {upload_time_ms} ms\t FileSize: {file_size} bytes')

    except FileNotFoundError as e:
        print(f'The local file {local_file_path} was not found!')
        logging.error(e)
        return None
    return "OK"



def download_and_log_from_s3(request_id, s3_bucket, s3_key, local_path):
    s3 = boto3.client('s3')
    file_name = os.path.basename(s3_key) # basename representa o nome do arquivo
    local_file_path = os.path.join(local_path, file_name)

    start_time = timeit.default_timer()
    s3.download_file(s3_bucket, s3_key, local_file_path)
    end_time = timeit.default_timer()
    download_time_ms = (end_time - start_time) * 1000
    file_size = os.stat(local_file_path).st_size
    
    print(f'Download Successful from S3! File {file_name} | {file_size} bytes | {download_time_ms} milissegundos')

    print(f'FILE_TRANSFER RequestId: {request_id}\t TransferType: consumed\t FileName: {file_name}\t Bucket: {s3_bucket}\t FilePath: {s3_key}\t LocalFilePath: {local_file_path}\t TransferDuration: {download_time_ms} ms\t FileSize: {file_size} bytes')

    return file_name
