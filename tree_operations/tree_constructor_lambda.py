from tree_constructor_core import *
import timeit

# O bucket e key de saída dos arquivos gerados nesta etapa
BUCKET_OUTPUT = 'mribeiro-bucket-output-tree'
S3_KEY_OUTPUT = ''

# Localização (temporária dentro da função lambda) dos arquivos de entrada utilizados pela função
PATH_INPUT = '/tmp/data/input/trees' # '/tmp' is lambda local folder

# Localização (temporária dentro da função lambda) dos arquivos gerados nesta etapa
PATH_OUTPUT = '/tmp/data/output/trees'

# Usado para escrever arquivos 'nopipe' durante o processo de validação
PATH_TMP = '/tmp'

# Localização do binário do Clustalw
PATH_CLUSTALW = '/opt/python/clustalw-2.1-linux-x86_64-libcppstatic'

# Formato das sequências
DATA_FORMAT = 'nexus' # newick ou nexus

def lambda_handler(event, context):
    
    request_id = context.aws_request_id
    
    print('******* Estado do ambiente de execução *******')
    print('pwd:', os.getcwd())
    # print('/:', os.listdir('/'))
    # print('/opt: ', os.listdir('/opt'))
    # print('/opt/python: ', os.listdir('/opt/python'))
    # print('/var/task: ', os.listdir('/var/task'))
    
    #
    # ## Limpeza arquivos temporários ##
    #
    remove_files(PATH_TMP)
    remove_files(PATH_INPUT) # limpar o input somente na execução via lambda
    remove_files(PATH_OUTPUT)


    #
    # ## PERCORRER E MANIPULAR DIRETORIO ##
    # 
    # get your bucket and key from event data
    data_rec = event['Records'][0]['s3']
    s3_bucket = data_rec['bucket']['name']

    # key representa o path + nome do arquivo que acionou o gatilho do lambda
    s3_key = data_rec['object']['key'] 
    print(f'S3_bucket: {s3_bucket} | S3_key: {s3_key}')

    #
    # download files from s3 bucket into lambda function
    #
    start_time = timeit.default_timer()

    file_name = download_and_log_from_s3(request_id, s3_bucket, s3_key, PATH_INPUT)

    end_time = timeit.default_timer()
    transfer_duration_ms = (end_time - start_time) * 1000
    
    files_count, files_size = get_num_files_and_size(PATH_INPUT)

    print(f'CONSUMED_FILES_INFO RequestId: {request_id}\t FilesCount: {files_count} files\t FilesSize: {files_size} bytes\t TransferDuration: {transfer_duration_ms} ms')

    ############################################

   
    #
    # ## Construção dos arquivos de árvores ##
    # 
    start_time = timeit.default_timer()

    tree_constructor(file_name, PATH_INPUT, PATH_TMP, PATH_OUTPUT, PATH_CLUSTALW, DATA_FORMAT)

    end_time = timeit.default_timer()
    tree_time_ms = (end_time - start_time) * 1000
    
    print(f'TREE_CONSTRUCTOR RequestId: {request_id}\t Duration: {tree_time_ms} ms')

    ############################################


    #
    # ## Copiar arquivos tree para o S3 ##
    #
    start_time = timeit.default_timer()

    for file_name in os.listdir(PATH_OUTPUT):
        # upload files from lambda function into s3
        upload_and_log_to_s3(request_id, BUCKET_OUTPUT, S3_KEY_OUTPUT, file_name, PATH_OUTPUT)
    
    end_time = timeit.default_timer()
    transfer_duration_ms = (end_time - start_time) * 1000
    
    files_count, files_size = get_num_files_and_size(PATH_OUTPUT)
    
    print(f'PRODUCED_FILES_INFO RequestId: {request_id}\t FilesCount: {files_count} files\t FilesSize: {files_size} bytes\t TransferDuration: {transfer_duration_ms} ms')

    ############################################    
        

    return "OK"

