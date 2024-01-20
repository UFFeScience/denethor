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
            print("Removed the file %s" % file_path)     
    else:
        print("Sorry, directory %s did not exist." % dir_path)
        os.makedirs(dir_path, exist_ok=True) # cria o diretório, caso não exista
        print("Directory %s was created!" % dir_path)


def directory_has_single_file(directory_path):
    if not os.path.isdir(directory_path):
        return False

    files = os.listdir(directory_path)
    if len(files) != 1:
        return False

    return True


def upload_and_log_to_s3(request_id, s3, s3_bucket, s3_keys, file_name, file_path):
    # basename representa o nome do arquivo
    s3_key_upload = os.path.join(s3_key, file_name)
    file_name_with_path = os.path.join(file_path, file_name)

    print('=> Upload file to S3')
    print(f's3_bucket_upload: {s3_bucket}')
    print(f's3_key_upload: {s3_key_upload}')
    print(f'file_name_with_path: {file_name_with_path}')

    
    try:
        start_time = timeit.default_timer()

        s3.upload_file(file_name_with_path, s3_bucket, s3_key_upload)
        print("Upload Successful: {file_name}")

        end_time = timeit.default_timer()
        upload_time_ms = (end_time - start_time) * 1000
        
        print("Tempo de upload do arquivo para o S3:", upload_time_ms, "milissegundos")

        file_size = os.stat(file_name_with_path).st_size

        print(f"O tamanho do arquivo {file_name} é: {file_size} bytes")
    
        print(f"FILE_UPLOAD RequestId: {request_id}\t FileName: {file_name}\t Bucket: {s3_bucket}\t FilePath: {s3_key_upload}\t Duration: {upload_time_ms} ms\t FileSize: {file_size} bytes")

    except FileNotFoundError as e:
        print(f"The local file {file_name_with_path} was not found!")
        logging.error(e)
        return None

def download_and_log_from_s3(request_id, s3, s3_bucket, s3_key, path_input):
    # basename representa o nome do arquivo
    file_name = os.path.basename(s3_key)
    file_name_with_path = os.path.join(path_input, file_name)

    start_time = timeit.default_timer()

    s3.download_file(s3_bucket, s3_key, file_name_with_path)

    end_time = timeit.default_timer()
    download_time_ms = (end_time - start_time) * 1000

    print("Tempo de download do arquivo a partir o S3:", download_time_ms, "milissegundos")

    file_size = os.stat(file_name_with_path).st_size

    print(f"O tamanho do arquivo {file_name} é: {file_size} bytes")

    print(f"FILE_DOWNLOAD RequestId: {request_id}\t FileName: {file_name}\t Bucket: {s3_bucket}\t FilePath: {s3_key}\t Duration: {download_time_ms} ms\t FileSize: {file_size} bytes")
    
    return file_name
