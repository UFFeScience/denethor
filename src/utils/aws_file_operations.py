import boto3
import os

def upload_files_to_aws_s3(params):
    """
    Uploads files to an AWS S3 bucket.

    Args:
        params (dict): A dictionary containing the following keys:
            - bucket (str): The name of the S3 bucket.
            - key (str): The key prefix for the uploaded files.
            - dataFiles (dict): A dictionary containing the following keys:
                - files (list): A list of file names to be uploaded.
                - path (str): The path to the directory containing the files.

    Returns:
        None
    """
    s3 = boto3.client('s3')
    bucket = params['bucket']
    key = params['key']
    files = params['input_files_name']
    path = params['input_files_path']
    for file_name in files:
        # Full path to the file
        file_path = os.path.join(path, file_name)
        file_key = os.path.join(key, file_name)
        # Upload the file to S3
        s3.upload_file(file_path, bucket, file_key)
        print(f'File {file_key} uploaded to {bucket}')


def download_files_from_aws_s3(params):
    """
    Downloads files from an S3 bucket to a specified local directory.

    Args:
        params (dict): A dictionary containing the following parameters:
            - bucket (str): The name of the S3 bucket.
            - key (str): The key prefix for the files in the S3 bucket.
            - dataFiles (dict): A dictionary containing the list of files to download.
                - files (list): A list of file names to download.
            - downloadPath (str): The local directory path where the files will be downloaded.
            - executionId (str): An execution ID used to replace a placeholder in the download path.

    Returns:
        None

    Raises:
        botocore.exceptions.NoCredentialsError: If AWS credentials are not found.
        botocore.exceptions.ParamValidationError: If the input parameters are invalid.
        botocore.exceptions.EndpointConnectionError: If there is an error connecting to the S3 endpoint.
        botocore.exceptions.ClientError: If there is an error downloading the file from S3.

    """
    s3 = boto3.client('s3')
    bucket = params['bucket']
    key = params['key']
    files = params['files']
    downloadPath = params['downloadPath']
    downloadPath.replace('[executionId]', params['executionId'])
    for file_name in files:
        # Full path to the file
        file_path = os.path.join(downloadPath, file_name)
        file_key = os.path.join(key, file_name)
        # Download the file from S3
        s3.download_file(bucket, file_key, file_path)
        print(f'File {file_key} downloaded from {bucket}')
