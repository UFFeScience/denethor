from tree_sub_find_core import *
import boto3
import time
import timeit


# Substitua pelo caminho de entrada dos arquivos
PATH_BASE = '/tmp' # '/tmp' is lambda local folder
PATH_DATA = os.path.join(PATH_BASE, 'data')

# O bucket de entrada dos arquivos gerados pelo tree_constructor
BUCKET_INPUT = 'mribeiro-bucket-output-tree'

# O bucket de saída dos arquivos gerados nesta etapa
BUCKET_OUTPUT = 'mribeiro-bucket-output-subtree'
S3_KEY_OUTPUT = ''

# Localização dos arquivos de entrada utilizados pela função
PATH_INPUT_LOCAL = os.path.join(PATH_DATA, 'input', 'trees')

# Localização dos arquivos gerados nesta etapa
PATH_OUTPUT_LOCAL = os.path.join(PATH_DATA, 'output', 'subtrees')

DATA_FORMAT = 'nexus' # newick ou nexus

s3 = boto3.client('s3')

def lambda_handler(event, context):
    
    request_id = context.aws_request_id

    print("******* Estado do ambiente de execução *******")
    print('pwd:', os.getcwd())
    print('/tmp:', os.listdir("/tmp"))
    print('/opt: ', os.listdir("/opt"))
    print('/opt/python: ', os.listdir("/opt/python"))
    print('/var/task: ', os.listdir("/var/task"))

    #
    # ## Limpeza arquivos temporários ##
    #
    remove_files(PATH_INPUT_LOCAL) #comentar na execução local
    remove_files(PATH_OUTPUT_LOCAL)


    s3_bucket = BUCKET_INPUT # por enquanto esse bucket está fixo, depois tentar passar via request
    
    #
    # List and downloads the tree files from bucket
    #
    start_time = timeit.default_timer()
    
    response = s3.list_objects_v2(Bucket=s3_bucket, Prefix='', StartAfter='', Delimiter='/')
    s3_files = response["Contents"]
    for s3_file in s3_files:
        # key representa o path + nome do arquivo do s3
        s3_key = s3_file["Key"]
        print('downloading file from s3:', s3_key)

        # download files from s3 into lambda function
        tree_file = download_and_log_from_s3(request_id, s3, s3_bucket, s3_key, PATH_INPUT_LOCAL)

    end_time = timeit.default_timer()
    transfer_duration_ms = (end_time - start_time) * 1000
    
    files_count, files_size = get_num_files_and_size(PATH_INPUT_LOCAL)

    print(f"CONSUMED_FILES_INFO RequestId: {request_id}\t FilesCount: {files_count} files\t FilesSize: {files_size} bytes\t TransferDuration: {transfer_duration_ms} ms")

    ############################################


    #
    # ## Construção dos arquivos de subárvores ##
    # 
    start_time = timeit.default_timer()

    subtree_matrix = []
    for tree_file in os.listdir(PATH_INPUT_LOCAL):
        subtree = subtree_constructor(tree_file, PATH_INPUT_LOCAL, PATH_OUTPUT_LOCAL, DATA_FORMAT)
        subtree_matrix.append(subtree)
    
    end_time = timeit.default_timer()
    subtree_time_ms = (end_time - start_time) * 1000
    
    print(f"SUBTREE_FILES_CREATE RequestId: {request_id}\t Duration: {subtree_time_ms} ms")

    ############################################
    
    
    # para evitar: "PermissionError: [Errno 13] Permission denied" ao tentar abrir os arquivos logo após terem sido escritos
    time.sleep(0.100)


    #
    # ## Criação do dicionário de similariadades de subárvore ##
    #
    start_time = timeit.default_timer()
    
    dict_maf_database, max_maf = create_maf_database(subtree_matrix, PATH_OUTPUT_LOCAL, DATA_FORMAT)
    
    end_time = timeit.default_timer()
    maf_time_ms = (end_time - start_time) * 1000
    
    print("Tempo de criação do maf_database:", maf_time_ms, "milissegundos")
    print('max_maf:', max_maf)

    print(f"MAF_DATABASE_CREATE RequestId: {request_id}\t MaxMaf: {max_maf}\t Duration: {maf_time_ms} ms\t MafDatabase: {dict_maf_database}")

    ############################################


    #
    # ## Copiar arquivos tree para o S3 ##
    #
    start_time = timeit.default_timer()

    for tree_file in os.listdir(PATH_OUTPUT_LOCAL):
        # upload files from lambda function into s3
        upload_and_log_to_s3(request_id, s3, BUCKET_OUTPUT, S3_KEY_OUTPUT, tree_file, PATH_OUTPUT_LOCAL)
        
    end_time = timeit.default_timer()
    transfer_duration_ms = (end_time - start_time) * 1000
    
    files_count, files_size = get_num_files_and_size(PATH_OUTPUT_LOCAL)
    
    print(f"PRODUCED_FILES_INFO RequestId: {request_id}\t FilesCount: {files_count} files\t FilesSize: {files_size} bytes\t TransferDuration: {transfer_duration_ms} ms")

    ############################################
    
    return "OK"
