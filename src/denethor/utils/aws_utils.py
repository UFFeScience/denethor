import os, boto3, timeit, logging
from denethor.utils import utils as du
from denethor import constants as const

s3 = boto3.client('s3')


##
# Consumed (download) Files
##
def handle_consumed_files(request_id: str, 
                          provider: str,
                          file_list: list, 
                          file_path_local: str, 
                          s3_bucket: str,
                          s3_key: str,
                          logger: logging.Logger) -> dict:
    total_download_duration_ms = 0
    total_files_size = 0
    total_files_count = 0
    download_details = []
    
    file_list_flat = du.flatten_list(file_list)

    # Download file from s3 bucket into lambda function
    for file_name in file_list_flat:
        duration_ms = 0
        file_path_local_full = os.path.join(file_path_local, file_name)
        file_path_s3_full = os.path.join(s3_key, file_name)
        
        if provider == const.AWS_LAMBDA:
            # TODO: avaliar se essa solução é definitiva
            # Passar um parâmetro de local cache? Acho melhor a ideia do zip...
            # se o arquivo estiver disponível localmente, não fazer o download,
            # mas copiar para o file_path_local
            # file_subtree = os.path.join("subtree_files", file_name)  
            # if os.path.exists(file_subtree):
            #     os.system(f"cp {file_subtree} {file_path_local_full}")
            #     logger.info(f"File {file_name} already exists in local path. Skipping download.")
            #     duration_ms = 0
            # else:
            duration_ms = download_single_file_from_s3(file_name, file_path_local, s3_bucket, s3_key)
            total_download_duration_ms += duration_ms
        
        file_size = get_file_size(file_path_local_full)
        total_files_size += file_size
        total_files_count += 1
        download_details.append({
            "file_name": file_name,
            "file_size": file_size,
            "download_duration_ms": duration_ms
        })
        
        logger.info(f"FILE_TRANSFER RequestId: {request_id}\t TransferType: consumed\t Action: download_from_s3\t FileName: {file_name}\t Bucket: {s3_bucket}\t FilePath: {file_path_s3_full}\t FilePathLocal: {file_path_local}\t FileSize: {file_size} bytes\t TransferDuration: {duration_ms} ms")
    
    logger.info(f"CONSUMED_FILES_INFO RequestId: {request_id}\t FilesCount: {total_files_count} files\t FilesSize: {total_files_size} bytes\t TransferDuration: {total_download_duration_ms} ms\t ConsumedFiles: {file_list_flat}")
    
    download_rate_mbps = calculate_transfer_rate_mbps(total_download_duration_ms, total_files_size)

    return {
        "total_download_duration_ms": total_download_duration_ms,
        "total_files_count": total_files_count,
        "total_files_size": total_files_size,
        "download_rate_mbps": download_rate_mbps,
        "files": download_details
    }
    

##
# Download single file from S3
##
def download_single_file_from_s3(file_name: str, 
                                 file_path: str, 
                                 s3_bucket: str, 
                                 s3_key: str) -> float:

    start_time = timeit.default_timer()
    
    validade_required_params(file_name, file_path, s3_bucket)
    
    # dependendo da forma que a requisição é feita, o nome do arquivo pode já estar incluso na s3_key
    if not s3_key.endswith(file_name):
        s3_key = os.path.join(s3_key, file_name)

    local_file = os.path.join(file_path, file_name)

    s3.download_file(s3_bucket, s3_key, local_file)
    
    end_time = timeit.default_timer()
    download_duration_ms = (end_time - start_time) * 1000

    return download_duration_ms
      



##
# Produced (upload) Files
##
def handle_produced_files(request_id: str, 
                          provider: str,
                          file_list: list, 
                          file_path_local: str, 
                          s3_bucket: str,
                          s3_key: str,
                          logger: logging.Logger) -> dict:
    total_upload_duration_ms = 0
    total_files_size = 0
    total_files_count = 0
    upload_details = []
    file_list_flat = du.flatten_list(file_list)

    # Upload files from lambda function into s3 bucket
    for file_name in file_list_flat:
        duration_ms = 0
        file_path_local_full = os.path.join(file_path_local, file_name)
        file_path_s3_full = os.path.join(s3_key, file_name)
        
        if provider == const.AWS_LAMBDA:
            duration_ms = upload_single_file_to_s3(file_name, file_path_local, s3_bucket, s3_key)
            total_upload_duration_ms += duration_ms
        
        file_size = get_file_size(file_path_local_full)
        total_files_size += file_size
        total_files_count += 1
        upload_details.append({
            "file_name": file_name,
            "file_size": file_size,
            "upload_duration_ms": duration_ms
        })
        
        logger.info(f"FILE_TRANSFER RequestId: {request_id}\t TransferType: produced\t Action: upload_to_s3\t FileName: {file_name}\t Bucket: {s3_bucket}\t FilePath: {file_path_s3_full}\t FilePathLocal: {file_path_local_full}\t FileSize: {file_size} bytes\t TransferDuration: {duration_ms} ms")

    logger.info(f"PRODUCED_FILES_INFO RequestId: {request_id}\t FilesCount: {total_files_count} files\t FilesSize: {total_files_size} bytes\t TransferDuration: {total_upload_duration_ms} ms\t Provider: {provider}\t ProducedFiles: {file_list_flat}")
    
    upload_rate_mbps = calculate_transfer_rate_mbps(total_upload_duration_ms, total_files_size)

    return {
        "total_upload_duration_ms": total_upload_duration_ms,
        "total_files_count": total_files_count,
        "total_files_size": total_files_size,
        "upload_rate_mbps": upload_rate_mbps,
        "files": upload_details
    }
  
##
# Upload single file to S3
##
def upload_single_file_to_s3(file_name: str, 
                             file_path: str, 
                             s3_bucket: str, 
                             s3_key: str) -> float:
    start_time = timeit.default_timer()
    
    validade_required_params(file_name, file_path, s3_bucket)
    
    try:
        s3_key_upload = os.path.join(s3_key, file_name)
        local_file = os.path.join(file_path, file_name)

        s3.upload_file(local_file, s3_bucket, s3_key_upload)

        end_time = timeit.default_timer()
        upload_duration_ms = (end_time - start_time) * 1000

    except FileNotFoundError as e:
        logging.error(e)
        raise e
    
    return upload_duration_ms



##
# Auxiliar and Validation Functions
##
def calculate_total_files_and_size(files: list, path: str) -> tuple[int, int]:
    """
    Get file metadata from a directory.
    Args:
        files (list): List of file names to check.
        path (str): Path to the directory.
    Returns:
        tuple: Total file count and total file size.
    """
    if not os.path.exists(path):
        raise ValueError(f"Path {path} does not exist!")
    if not os.path.isdir(path):
        raise ValueError(f"Path {path} is not a directory!")
    if not files:
        raise ValueError(f"Files list is empty!")
    
    file_names = []
    total_file_count = 0
    total_file_size = 0
    for file in os.listdir(path):
        fp = os.path.join(path, file)
        if os.path.isfile(fp) and (files is None or file in files):
            total_file_count += 1
            total_file_size += os.path.getsize(fp)
            file_names.append(file)
    
    return total_file_count, total_file_size

def get_file_size(file_path: str) -> int:
    """
    Retrieve the size of a file in bytes.
    Args:
        file_path (str): Path to the file.
    Returns:
        int: Size of the file in bytes.
    """
    if not os.path.exists(file_path):
        raise ValueError(f"File {file_path} does not exist!")
    if not os.path.isfile(file_path):
        raise ValueError(f"Path {file_path} is not a file!")
    
    return os.path.getsize(file_path)


# List files in S3 bucket
def list_files_in_s3(s3_bucket: str, s3_key: str) -> list:
    """
    List files in an S3 bucket.
    Args:
        s3_bucket (str): Name of the S3 bucket.
        s3_key (str): Key prefix to filter files.
    Returns:
        list: List of file names in the S3 bucket.
    """
    if s3_bucket is None or s3_bucket == '':
        raise ValueError('s3_bucket cannot be None when listing files from S3!')
    
    if s3_key is None or s3_key == '':
        raise ValueError('s3_key cannot be None when listing files from S3!')

    paginator = s3.get_paginator('list_objects_v2')
    response_iterator = paginator.paginate(Bucket=s3_bucket, Prefix=s3_key)
    
    file_list = []
    for response in response_iterator:
        if 'Contents' in response:
            for obj in response['Contents']:
                file_list.append(obj['Key'])
    
    return file_list


def validade_required_params(file_name: str, file_path: str, s3_bucket: str) -> None:
    if file_name is None or file_name == '':
        raise ValueError('file_name cannot be None when downloading/uploading from S3!')
    
    if file_path is None or file_path == '':
        raise ValueError('file_path cannot be None when downloading/uploading from S3!')
    
    if not os.path.exists(file_path):
        raise ValueError(f"file_path:{file_path} does not exist!")

    if s3_bucket is None or s3_bucket == '':
        raise ValueError('s3_bucket cannot be None when downloading/uploading from S3!')

def calculate_transfer_rate_mbps(total_duration_ms: int, total_files_size_bytes: int) -> float:
    """
    Calculate the transfer rate (upload or download) in Mbps.
    Args:
        total_duration_ms (int): Total transfer duration in milliseconds.
        total_files_size_bytes (int): Total size of files in bytes.
    Returns:
        float: Transfer rate in Mbps.
    """
    if total_duration_ms <= 0:
        raise ValueError("Total transfer duration must be greater than 0.")
    if total_files_size_bytes <= 0:
        raise ValueError("Total file size must be greater than 0.")
    
    return (total_files_size_bytes * 8) / (total_duration_ms / 1000 * 1_000_000)

