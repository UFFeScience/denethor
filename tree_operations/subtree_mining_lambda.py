from tree_operations.subtree_mining_core import *
from datetime import datetime

TMP_PATH = '/tmp' # '/tmp' is lambda local folder

INPUT_PATH = '/tmp/input' 

OUTPUT_PATH = '/tmp/subtrees'

# Formato das sequências
DATA_FORMAT = 'nexus' # newick ou nexus


def handler(event, context):
    
    request_id = context.aws_request_id

    print('******* Estado do ambiente de execução *******')
    print(f'Start time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('pwd:', os.getcwd())
    print('/tmp:', os.listdir('/tmp'))
    print('/opt: ', os.listdir('/opt'))
    print('/opt/python: ', os.listdir('/opt/python'))
    print('/var/task: ', os.listdir('/var/task'))

    #
    # ## Limpeza arquivos temporários ##
    #
    remove_files(TMP_PATH)
    remove_files(INPUT_PATH) # limpar o input somente na execução via lambda
    remove_files(OUTPUT_PATH)


    # Obter o bucket de entrada, a lista de arquivos e o bucket de saída do payload
    input_bucket = event['inputBucket']
    output_bucket = event['outputBucket']
    output_key = event['outputKey']
    input_files = event['files']

    #
    # ## Download multiple files from s3 bucket into lambda function
    #
    download_duration_ms = download_and_log_multiple_files_from_s3(request_id, input_bucket, INPUT_PATH, input_files, DATA_FORMAT)
    files_count, files_size = get_num_files_and_size(INPUT_PATH)
    consumed_files = os.listdir(INPUT_PATH)
    print(f'CONSUMED_FILES_INFO RequestId: {request_id}\t FilesCount: {files_count} files\t FilesSize: {files_size} bytes\t TransferDuration: {download_duration_ms} ms\t ConsumedFiles: {consumed_files}')

    ############################################


    #
    # ## Construção dos arquivos de subárvores ##
    # 
    total_subtree_duration_ms = 0
    subtree_matrix = []
    for tree_file in os.listdir(INPUT_PATH):
        subtree, subtree_duration_ms = subtree_constructor(tree_file, INPUT_PATH, OUTPUT_PATH, DATA_FORMAT)
        subtree_matrix.append(subtree)
        total_subtree_duration_ms += subtree_duration_ms

    print(f'SUBTREE_CONSTRUCTOR RequestId: {request_id}\t Duration: {total_subtree_duration_ms} ms')

    ############################################
    
    
    # para evitar: 'PermissionError: [Errno 13] Permission denied' ao tentar abrir os arquivos logo após terem sido escritos
    time.sleep(0.100)


    #
    # ## Criação do dicionário de similariadades de subárvore ##
    #
    start_time = timeit.default_timer()
    
    dict_maf_database, max_maf = maf_database_create(subtree_matrix, OUTPUT_PATH, DATA_FORMAT)
    
    end_time = timeit.default_timer()
    maf_time_ms = (end_time - start_time) * 1000
    
    print(f'Tempo de criação do maf_database: {maf_time_ms} milissegundos')
    print(f'max_maf: {max_maf}')

    print(f'MAF_DATABASE_CREATE RequestId: {request_id}\t MaxMaf: {max_maf}\t Duration: {maf_time_ms} ms\t MafDatabase: {dict_maf_database}')

    ############################################


    #
    # ## Copiar arquivos tree para o S3 ##
    #
    produced_files = os.listdir(OUTPUT_PATH)
    upload_duration_ms = upload_and_log_multiple_files_to_s3(request_id, output_bucket, output_key, OUTPUT_PATH, produced_files)
    files_count, files_size = get_num_files_and_size(OUTPUT_PATH)
    print(f'PRODUCED_FILES_INFO RequestId: {request_id}\t FilesCount: {files_count} files\t FilesSize: {files_size} bytes\t TransferDuration: {upload_duration_ms} ms\t ProducedFiles: {produced_files}')

    ############################################
    
    return 'OK'


