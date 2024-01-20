from tree_sub_find_core import *
import boto3
import time
import timeit


# Substitua pelo caminho de entrada dos arquivos
PATH_BASE = 'tmp' # '/tmp' is lambda local folder
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
    # print('/:', os.listdir("/"))
    # print('/opt: ', os.listdir("/opt"))
    # print('/opt/python: ', os.listdir("/opt/python"))
    # print('/var/task: ', os.listdir("/var/task"))

    #
    # ## Limpeza arquivos temporários ##
    #
    remove_files(PATH_INPUT_LOCAL) #comentar na execução local
    remove_files(PATH_OUTPUT_LOCAL)


    #
    # ## PERCORRER E MANIPULAR DIRETORIO ##
    # 
    
    s3_bucket = BUCKET_INPUT # por enquanto esse bucket está fixo, depois tentar passar via request
    
    #
    # List the tree files from bucket
    #
    response = s3.list_objects_v2(Bucket=s3_bucket, Prefix='', StartAfter='')
    s3_files = response["Contents"]
    for s3_file in s3_files:
        # key representa o path + nome do arquivo do s3
        s3_key = s3_file["Key"]
        print('file from s3:', s3_key)

        # download files from s3 into lambda function
        file_name = download_and_log_from_s3(request_id, s3, s3_bucket, s3_key, PATH_INPUT_LOCAL)

    
    #
    # ## PERCORRER E MANIPULAR DIRETORIO ##
    # 

    # matriz com todas as subárvores
    subtree_matrix = []

    # Diretório de entrada de árvores
    files = os.listdir(PATH_INPUT_LOCAL)

    for file_name in files:
        print("Reading file %s" % file_name)     
        file_path = os.path.join(PATH_INPUT_LOCAL, file_name)
        
        subtree = sub_tree_constructor(file_path, file_name, PATH_OUTPUT_LOCAL, DATA_FORMAT)
        subtree_matrix.append(subtree)
    
    # para evitar: "PermissionError: [Errno 13] Permission denied" ao tentar abrir os arquivos logo após terem sido escritos
    time.sleep(0.100)

    subtree_matrix = fill_matrix(subtree_matrix, value=None)

    dict_maf_database, max_maf = create_maf_database(subtree_matrix, PATH_OUTPUT_LOCAL, DATA_FORMAT)

    print('max_maf:', max_maf)
    print('Final dict_maf_database:', dict_maf_database)

    #
    # ## Copiar arquivos tree para o S3 ##
    #
    for file_name in os.listdir(PATH_OUTPUT_LOCAL):
        # upload files from lambda function into s3
        upload_and_log_to_s3(request_id, s3, BUCKET_OUTPUT, S3_KEY_OUTPUT, file_name, PATH_OUTPUT_LOCAL)
        
    return "OK"