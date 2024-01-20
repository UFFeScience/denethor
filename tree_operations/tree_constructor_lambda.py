from tree_operations.tree_constructor_core import *
import timeit
import boto3

# Substitua pelo caminho de entrada dos aquivos
PATH_BASE = 'tmp' # '/tmp' is lambda local folder
PATH_DATA = os.path.join(PATH_BASE, 'data')

# O bucket de entrada será recebido pelo trigger
# BUCKET_INPUT = 'mribeiro-bucket-input'

# O bucket de saída dos arquivos gerados nesta etapa
BUCKET_OUTPUT = 'mribeiro-bucket-output-tree'
S3_KEY_OUTPUT = ''

# Localização dos arquivos de entrada utilizados pela função
PATH_INPUT_LOCAL = os.path.join(PATH_DATA, 'input', 'trees')

# Localização dos arquivos gerados nesta etapa
PATH_OUTPUT_LOCAL = os.path.join(PATH_DATA, 'output', 'trees')


# Usado para escrever arquivos 'nopipe' durante o processo de validação
# Não devemos escrever na pasta 'input' do S3 pois acarretaria na invocação recursiva da função lambda
PATH_TMP = PATH_MAF = PATH_BASE

# Localização do binário do Clustalw
PATH_CLUSTALW = os.path.join('/', 'opt', 'python', 'clustalw-2.1-linux-x86_64-libcppstatic')

# Formato das sequências
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
    remove_files(PATH_TMP)
    remove_files(PATH_MAF)
    remove_files(PATH_INPUT_LOCAL) #comentar na execução local
    remove_files(PATH_OUTPUT_LOCAL)


    #
    # ## PERCORRER E MANIPULAR DIRETORIO ##
    # 
    # get your bucket and key from event data
    data_rec = event['Records'][0]['s3']
    s3_bucket = data_rec['bucket']['name']
    print("S3_bucket:", s3_bucket)

    # key representa o path + nome do arquivo que acionou o gatilho do lambda
    s3_key = data_rec['object']['key'] 
    print("S3_key:", s3_key)

    # download files from s3 into lambda function
    file_name = download_and_log_from_s3(request_id, s3, s3_bucket, s3_key, PATH_INPUT_LOCAL)

    # constructor_tree(path_in_fasta, path_out_aln, path_out_dnd, path_out_tree)
    constructor_tree(file_name, PATH_INPUT_LOCAL, PATH_TMP, PATH_OUTPUT_LOCAL, PATH_CLUSTALW, DATA_FORMAT)

   
    #
    # ## Copiar arquivos tree para o S3 ##
    #
    for file_name in os.listdir(PATH_OUTPUT_LOCAL):
        # upload files from lambda function into s3
        upload_and_log_to_s3(request_id, s3, BUCKET_OUTPUT, S3_KEY_OUTPUT, file_name, PATH_OUTPUT_LOCAL)
        
        

    return "OK"

