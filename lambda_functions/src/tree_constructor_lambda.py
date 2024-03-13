from datetime import datetime
from tree_constructor_core import *
from file_utils import *

TMP_PATH = '/tmp' # Usado para escrever arquivos 'nopipe' durante o processo de validação
INPUT_PATH = '/tmp/input' # '/tmp' is lambda local folder
OUTPUT_PATH = '/tmp/trees' # '/tmp' is lambda local folder
CLUSTALW_PATH = '/opt/python/clustalw-2.1-linux-x86_64-libcppstatic'
DATA_FORMAT = 'nexus' # Formato das sequências: newick ou nexus

def handler(event, context):

    request_id = context.aws_request_id
    
    print("******* Estado do ambiente de execução *******")
    print(f'Start time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('pwd:', os.getcwd())
    print('/tmp:', os.listdir('/tmp'))
    print('/opt: ', os.listdir('/opt'))
    print('/opt/python: ', os.listdir('/opt/python'))
    print('/var/task: ', os.listdir('/var/task'))
    
    ## Limpeza arquivos antigos ##
    remove_files(TMP_PATH)
    remove_files(INPUT_PATH) # limpar na execução via lambda, pois é o path temporário local
    remove_files(OUTPUT_PATH)

    # Obter o bucket de entrada, arquivo e o bucket de saída do payload
    input_bucket = event['inputBucket']
    input_file = event['file']
    output_bucket = event['outputBucket']
    output_key = event['outputKey']

    ## Download file from s3 bucket into lambda function
    download_duration_ms = download_and_log_single_file_from_s3(request_id, input_bucket, input_file, INPUT_PATH)
    files_count, files_size = get_num_files_and_size(INPUT_PATH)
    print(f'CONSUMED_FILES_INFO RequestId: {request_id}\t FilesCount: {files_count} files\t FilesSize: {files_size} bytes\t TransferDuration: {download_duration_ms} ms\t ConsumedFiles: {input_file}')

    ############################################


    ## Construção dos arquivos de árvores ##
    tree_duration_ms = tree_constructor(input_file, INPUT_PATH, TMP_PATH, OUTPUT_PATH, CLUSTALW_PATH, DATA_FORMAT)
    print(f'TREE_CONSTRUCTOR RequestId: {request_id}\t Duration: {tree_duration_ms} ms')

    ############################################


    ## Copiar arquivos tree para o S3 ##
    produced_files = os.listdir(OUTPUT_PATH)
    upload_duration_ms = upload_and_log_multiple_files_to_s3(request_id, output_bucket, output_key, OUTPUT_PATH, produced_files)
    files_count, files_size = get_num_files_and_size(OUTPUT_PATH)
    print(f'PRODUCED_FILES_INFO RequestId: {request_id}\t FilesCount: {files_count} files\t FilesSize: {files_size} bytes\t TransferDuration: {upload_duration_ms} ms\t ProducedFiles: {produced_files}')

    ############################################    
        
    return "OK"
