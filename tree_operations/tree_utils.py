import os
import logging
import boto3

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


def upload_file_to_S3(file_path, s3_bucket, s3_key, s3):
    
    print('=> Upload file to S3')
    print(f's3_bucket_upload: {s3_bucket}')
    print(f's3_key_upload: {s3_key}')
    print(f'file_upload: {file_path}')
    
    try:
        s3.upload_file(file_path, s3_bucket, s3_key)
        print("Upload Successful") #,url)

    except FileNotFoundError as e:
        print("The local file %s was not found" % file_path)
        logging.error(e)
        return None