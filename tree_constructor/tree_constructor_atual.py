from tree_constructor_core import *
import timeit
import boto3

# Substitua pelo caminho de entrada dos aquivos
# O bucket e path de entrada serão recebidos pelo trigger
# BUCKET_INPUT = 'mribeiro-bucket-input'
# PATH_INPUT  = 'input' # Armazena arquivos de entrada

BUCKET_OUTPUT = 'mribeiro-bucket-output-tree'
PATH_OUTPUT = '' # Armazena os arquivos de árvores finais na raiz do 

# Usado para escrever arquivos 'nopipe' durante o processo de validação
# Não devemos escrever na pasta 'input' do S3 pois acarretaria na invocação recursiva da função lambda
PATH_TMP = PATH_MAF = '/tmp'  # '/tmp' is lambda local folder

# Armazena arquivos de entrada que chegam no S3
PATH_TMP_INPUT = '/tmp/input'

# Armazena os arquivos de árvores finais que serão copiados para o S3
PATH_TMP_OUTPUT = '/tmp/trees'

PATH_CLUSTALW = '/opt/python/clustalw-2.1-linux-x86_64-libcppstatic'

# Formato das sequências
DATA_FORMAT = 'nexus' # newick ou nexus

s3 = boto3.client('s3')

def lambda_handler(event, context):
    
    request_id = context.aws_request_id
    
    # print("Estado do ambiente de execução")
    # print('pwd:', os.getcwd())
    # print('/:', os.listdir("/"))
    # print('/opt: ', os.listdir("/opt"))
    # print('/opt/python: ', os.listdir("/opt/python"))
    # print('/var/task: ', os.listdir("/var/task"))
    
    #
    # ## Limpeza arquivos temporários ##
    #
    remove_files(PATH_TMP)
    remove_files(PATH_MAF)
    remove_files(PATH_TMP_INPUT) #comentar na execução local
    remove_files(PATH_TMP_OUTPUT)


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

    # basename representa o nome do arquivo
    name_file = os.path.basename(s3_key)
    name_file_path = os.path.join(PATH_TMP_INPUT, name_file)
   

    start_time = timeit.default_timer()
    
    s3.download_file(s3_bucket, s3_key, name_file_path)
    
    end_time = timeit.default_timer()
    download_time_ms = (end_time - start_time) * 1000

    print("Tempo de dowload do arquivo para o S3:", download_time_ms, "milissegundos")
    
    
    file_size = os.stat(name_file_path).st_size

    print(f"O tamanho do arquivo {name_file} é: {file_size} bytes")
   
    print(f"FILE_DOWNLOAD RequestId: {request_id}\t FileName: {name_file}\t Bucket: {s3_bucket}\t FilePath: {s3_key}\t Duration: {download_time_ms} ms\t FileSize: {file_size} bytes")

    # constructor_tree(path_in_fasta, path_out_aln, path_out_dnd, path_out_tree)
    constructor_tree(name_file, PATH_TMP_INPUT, PATH_TMP, PATH_TMP_OUTPUT, PATH_CLUSTALW, DATA_FORMAT)

   
    #
    # ## Copiar arquivos tree para o S3 ##
    #
    dir_trees = os.path.join(PATH_TMP_OUTPUT)
    
    for tree_file_name in os.listdir(dir_trees):
        tree_file_path = os.path.join(dir_trees, tree_file_name)
        s3_output_key = os.path.join(PATH_OUTPUT, tree_file_name)
        
        # print("tree_file_name:", tree_file_name)
        print("tree_file_path:", tree_file_path)

        start_time = timeit.default_timer()
        
        upload_file_to_S3(tree_file_path, BUCKET_OUTPUT, s3_output_key)
        
        end_time = timeit.default_timer()
        upload_time_ms = (end_time - start_time) * 1000
        
        file_size = os.stat(tree_file_path).st_size

        print(f"O tamanho do arquivo {tree_file_name} é: {file_size} bytes")
    
        print(f"FILE_UPLOAD RequestId: {request_id}\t FileName: {tree_file_name}\t Bucket: {BUCKET_OUTPUT}\t FilePath: {s3_output_key}\t Duration: {upload_time_ms} ms\t FileSize: {file_size} ")


    return "OK"


def upload_file_to_S3(file_path, s3_bucket, s3_key):
    
    # print('Upload file to S3')
    print(f's3_bucket_upload: {s3_bucket}')
    print(f's3_key_upload: {s3_key}')
    print(f'file_upload: {file_path}')
    
    try:
        s3.upload_file(file_path, s3_bucket, s3_key)
        print("Upload Successful")
    except FileNotFoundError as e:
        print("The local file %s was not found" % file_path)
        logging.error(e)
        return None
