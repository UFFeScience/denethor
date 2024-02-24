import boto3
import os
import time
import json

# realiza o upload de arquivos para um bucket S3 / AWS
def upload_files_to_s3(params):
    s3 = boto3.client('s3')
    bucket = params['bucket']
    key = params['key']
    files = params['dataFiles']['files']
    path = params['dataFiles']['path']
    for file_name in files:
        # Caminho completo para o arquivo
        file_path = os.path.join(path, file_name)
        file_key = os.path.join(key, file_name)
        # Fazer o upload do arquivo para o S3
        s3.upload_file(file_path, bucket, file_key)
        print(f'File {file_key} uploaded to {bucket}')



def download_files_from_s3(params):
    s3 = boto3.client('s3')
    bucket = params['bucket']
    key = params['key']
    files = params['dataFiles']['files']
    downloadPath = params['downloadPath']
    downloadPath.replace('[executionId]', params['executionId'])
    for file_name in files:
        # Caminho completo para o arquivo
        file_path = os.path.join(downloadPath, file_name)
        file_key = os.path.join(key, file_name)
        # Fazer o download do arquivo do S3
        s3.download_file(bucket, file_key, file_path)
        print(f'File {file_key} downloaded from {bucket}')

