from tree_sub_find_core import *
import re
import boto3
import time
import timeit

# O bucket de entrada dos arquivos gerados pelo tree_constructor
# BUCKET_INPUT = 'mribeiro-bucket-output-tree'

# # O bucket e key de saída dos arquivos gerados nesta etapa
# BUCKET_OUTPUT = 'mribeiro-bucket-output-subtree'
# S3_KEY_OUTPUT = ''

PATH_TMP = '/tmp'

# Localização dos arquivos de entrada utilizados pela função
PATH_TMP_INPUT = '/tmp/input' # na execução local é output do tree_constructor

# Localização dos arquivos gerados nesta etapa
PATH_TMP_OUTPUT = '/tmp/output'

# Formato das sequências
DATA_FORMAT = 'nexus' # newick ou nexus


def lambda_handler(event, context):
    
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
    remove_files(PATH_TMP)
    remove_files(PATH_TMP_INPUT) # limpar o input somente na execução via lambda
    remove_files(PATH_TMP_OUTPUT)


    # s3_bucket = BUCKET_INPUT # por enquanto esse bucket está fixo, depois tentar passar via request
    

    # Obter o bucket de entrada, a lista de arquivos e o bucket de saída do payload
    input_bucket = event['inputBucket']
    output_bucket = event['outputBucket']
    output_key = event['outputKey']
    input_files = event['files']

    #
    # List and downloads the tree files from bucket
    #
    start_time = timeit.default_timer()
    
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=input_bucket, Prefix='', StartAfter='', Delimiter='/')
    
    all_matching_files = []  # para armazenar todos os objetos correspondentes

    for base_file_name in input_files:
        pattern = r'.*{}(_Inner\d+|)\.{}$'.format(base_file_name, DATA_FORMAT)
        matching_files = [item['Key'] for item in response['Contents'] if re.match(pattern, item['Key'])]
        all_matching_files.extend(matching_files)
        print(f'pattern: {pattern} | matching_files: {matching_files}')
    
    
    # for s3_file in response['Contents']:
    for s3_file_key in all_matching_files:
        # key representa o path + nome do arquivo do s3
        print(f'downloading file from s3: {s3_file_key}')

        # download files from s3 into lambda function
        tree_file = download_and_log_from_s3(request_id, input_bucket, s3_file_key, PATH_TMP_INPUT)

    end_time = timeit.default_timer()
    transfer_duration_ms = (end_time - start_time) * 1000
    
    files_count, files_size = get_num_files_and_size(PATH_TMP_INPUT)

    print(f'CONSUMED_FILES_INFO RequestId: {request_id}\t FilesCount: {files_count} files\t FilesSize: {files_size} bytes\t TransferDuration: {transfer_duration_ms} ms\t ConsumedFiles: {all_matching_files}')

    ############################################


    #
    # ## Construção dos arquivos de subárvores ##
    # 
    start_time = timeit.default_timer()

    subtree_matrix = []
    for tree_file in os.listdir(PATH_TMP_INPUT):
        subtree = subtree_constructor(tree_file, PATH_TMP_INPUT, PATH_TMP_OUTPUT, DATA_FORMAT)
        subtree_matrix.append(subtree)
    
    end_time = timeit.default_timer()
    subtree_time_ms = (end_time - start_time) * 1000
    print(f'Tempo de construção dos arquivos de subárvores: {subtree_time_ms} milissegundos')

    print(f'SUBTREE_CONSTRUCTOR RequestId: {request_id}\t Duration: {subtree_time_ms} ms')

    ############################################
    
    
    # para evitar: 'PermissionError: [Errno 13] Permission denied' ao tentar abrir os arquivos logo após terem sido escritos
    time.sleep(0.100)


    #
    # ## Criação do dicionário de similariadades de subárvore ##
    #
    start_time = timeit.default_timer()
    
    dict_maf_database, max_maf = maf_database_create(subtree_matrix, PATH_TMP_OUTPUT, DATA_FORMAT)
    
    end_time = timeit.default_timer()
    maf_time_ms = (end_time - start_time) * 1000
    
    print(f'Tempo de criação do maf_database: {maf_time_ms} milissegundos')
    print(f'max_maf: {max_maf}')

    print(f'MAF_DATABASE_CREATE RequestId: {request_id}\t MaxMaf: {max_maf}\t Duration: {maf_time_ms} ms\t MafDatabase: {dict_maf_database}')

    ############################################


    #
    # ## Copiar arquivos tree para o S3 ##
    #
    start_time = timeit.default_timer()

    produced_files = os.listdir(PATH_TMP_OUTPUT)

    for tree_file in produced_files:
        # upload files from lambda function into s3
        upload_and_log_to_s3(request_id, output_bucket, output_key, tree_file, PATH_TMP_OUTPUT)
        
    end_time = timeit.default_timer()
    transfer_duration_ms = (end_time - start_time) * 1000

    files_count, files_size = get_num_files_and_size(PATH_TMP_OUTPUT)
    
    print(f'PRODUCED_FILES_INFO RequestId: {request_id}\t FilesCount: {files_count} files\t FilesSize: {files_size} bytes\t TransferDuration: {transfer_duration_ms} ms\t ProducedFiles: {produced_files}')

    ############################################
    
    return 'OK'
