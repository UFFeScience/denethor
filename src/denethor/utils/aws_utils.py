import os, boto3, timeit, logging
from denethor.utils import utils as du
from denethor.constants import ExecutionProviderEnum as ep

s3 = boto3.client('s3')


##
# Consumed (download) Files
##
def handle_consumed_files(request_id: str, 
                          provider: str,
                          file_list: list, 
                          file_path: str, 
                          s3_bucket: str ="",
                          s3_key: str ="") -> None:
    download_duration_ms = 0
    file_list_flat = du.flatten_list(file_list)
    
    if provider == ep.AWS_LAMBDA:
        # Download file from s3 bucket into lambda function
        for file_name in file_list_flat:
            duration_ms = download_single_file_from_s3(request_id, file_name, file_path, s3_bucket, s3_key)
            download_duration_ms += duration_ms
    
    info = get_file_info(file_list_flat, file_path)      
    print(f"CONSUMED_FILES_INFO RequestId: {request_id}\t FilesCount: {info.get('files_count')} files\t FilesSize: {info.get('files_size')} bytes\t TransferDuration: {download_duration_ms} ms\t ConsumedFiles: {file_list_flat}")
    

##
# Download single file from S3
##
def download_single_file_from_s3(request_id: str, 
                                 file_name: str, 
                                 file_path: str, 
                                 s3_bucket: str, 
                                 s3_key: str) -> int:
    start_time = timeit.default_timer()
    
    validade_required_params(request_id, file_name, file_path, s3_bucket)
    
    # dependendo da forma que a requisição é feita, o nome do arquivo pode já estar incluso na s3_key
    if not s3_key.endswith(file_name):
        s3_key = os.path.join(s3_key, file_name)

    local_file = os.path.join(file_path, file_name)

    s3.download_file(s3_bucket, s3_key, local_file)
    
    end_time = timeit.default_timer()
    download_duration_ms = (end_time - start_time) * 1000
    file_size = os.stat(local_file).st_size

    print(f"FILE_TRANSFER RequestId: {request_id}\t TransferType: consumed\t Action: download_from_s3\t FileName: {file_name}\t Bucket: {s3_bucket}\t FilePath: {s3_key}\t LocalFilePath: {local_file}\t FileSize: {file_size} bytes\t TransferDuration: {download_duration_ms} ms")

    return download_duration_ms
      



##
# Produced (upload) Files
##
def handle_produced_files(request_id: str, 
                          provider: str,
                          file_list: list, 
                          file_path: str, 
                          s3_bucket: str ="",
                          s3_key: str ="") -> None:
    upload_duration_ms = 0
    file_list_flat = du.flatten_list(file_list)

    if provider == ep.AWS_LAMBDA:
        # Upload files from lambda function into s3 bucket
        for file_name in file_list_flat:
            duration_ms = upload_single_file_to_s3(request_id, file_name, file_path, s3_bucket, s3_key)
            upload_duration_ms += duration_ms

    info = get_file_info(file_list_flat, file_path)      
    print(f"PRODUCED_FILES_INFO RequestId: {request_id}\t FilesCount: {info.get('files_count')} files\t FilesSize: {info.get('files_size')} bytes\t TransferDuration: {upload_duration_ms} ms\t Provider: {provider}\t  ProducedFiles: {file_list_flat}")
  
##
# Upload single file to S3
##
def upload_single_file_to_s3(request_id: str, 
                             file_name: str, 
                             file_path: str, 
                             s3_bucket: str, 
                             s3_key: str) -> int:
    start_time = timeit.default_timer()
    
    validade_required_params(request_id, file_name, file_path, s3_bucket)
    
    try:
        s3_key_upload = os.path.join(s3_key, file_name)
        local_file = os.path.join(file_path, file_name)

        s3.upload_file(local_file, s3_bucket, s3_key_upload)

        end_time = timeit.default_timer()
        upload_duration_ms = (end_time - start_time) * 1000
        file_size = os.stat(local_file).st_size
        
        print(f"FILE_TRANSFER RequestId: {request_id}\t TransferType: produced\t Action: upload_to_s3\t FileName: {file_name}\t Bucket: {s3_bucket}\t FilePath: {s3_key_upload}\t LocalFilePath: {local_file}\t FileSize: {file_size} bytes\t TransferDuration: {upload_duration_ms} ms")

    except FileNotFoundError as e:
        print(f"The local file {local_file} was not found!")
        logging.error(e)
        raise e
    
    return upload_duration_ms




##
# Auxiliar and Validation Functions
##
def get_file_info(files: list, path: str) -> dict:
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


def validade_required_params(request_id: str, file_name: str, file_path: str, s3_bucket: str) -> None:
    if request_id is None or request_id == '':
        raise ValueError('request_id cannot be None when downloading/uploading from S3!')
    
    if file_name is None or file_name == '':
        raise ValueError('file_name cannot be None when downloading/uploading from S3!')
    
    if file_path is None or file_path == '':
        raise ValueError('file_path cannot be None when downloading/uploading from S3!')
    
    if not os.path.exists(file_path):
        raise ValueError(f"file_path:{file_path} does not exist!")

    if s3_bucket is None or s3_bucket == '':
        raise ValueError('s3_bucket cannot be None when downloading/uploading from S3!')
    