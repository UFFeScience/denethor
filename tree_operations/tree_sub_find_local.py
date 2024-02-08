from tree_sub_find_core import *
import time
import timeit

# O bucket de entrada dos arquivos gerados pelo tree_constructor
# BUCKET_INPUT = 'mribeiro-bucket-output-tree'

# # O bucket e key de saída dos arquivos gerados nesta etapa
# BUCKET_OUTPUT = 'mribeiro-bucket-output-subtree'
# S3_KEY_OUTPUT = ''

# Localização dos arquivos de entrada utilizados pela função
PATH_INPUT = 'tree_operations/data/output/trees' # na execução local é output do tree_constructor

# Localização dos arquivos gerados nesta etapa
PATH_OUTPUT = 'tree_operations/data/output/subtrees'

# Formato das sequências
DATA_FORMAT = 'nexus' # newick ou nexus


def lambda_handler(event, context):
    
    request_id = None

    print('******* Estado do ambiente de execução *******')
    print('pwd:', os.getcwd())

    #
    # ## Limpeza arquivos temporários ##
    #
    remove_files(PATH_OUTPUT)

    #
    # ## Construção dos arquivos de subárvores ##
    # 
    start_time = timeit.default_timer()

    subtree_matrix = []
    for tree_file in os.listdir(PATH_INPUT):
        subtree = subtree_constructor(tree_file, PATH_INPUT, PATH_OUTPUT, DATA_FORMAT)
        subtree_matrix.append(subtree)
    
    end_time = timeit.default_timer()
    subtree_time_ms = (end_time - start_time) * 1000
    print(f'Tempo de construção dos arquivos de subárvores: {subtree_time_ms} milissegundos')

    print(f'SUBTREE_CONSTRUCTOR RequestId: {request_id}\t Duration: {subtree_time_ms} ms')

    ############################################
    
    
    # para evitar: 'PermissionError: [Errno 13] Permission denied' ao tentar abrir os arquivos logo após terem sido escritos
    time.sleep(0.500)


    #
    # ## Criação do dicionário de similariadades de subárvore ##
    #
    start_time = timeit.default_timer()
    
    dict_maf_database, max_maf = maf_database_create(subtree_matrix, PATH_OUTPUT, DATA_FORMAT)
    
    end_time = timeit.default_timer()
    maf_time_ms = (end_time - start_time) * 1000
    
    print(f'Tempo de criação do maf_database: {maf_time_ms} milissegundos')
    print(f'max_maf: {max_maf}')

    print(f'MAF_DATABASE_CREATE RequestId: {request_id}\t MaxMaf: {max_maf}\t Duration: {maf_time_ms} ms\t MafDatabase: {dict_maf_database}')

    ############################################
    
    
    
    transfer_duration_ms = None
    files_count, files_size = get_num_files_and_size(PATH_OUTPUT)
    
    print(f'PRODUCED_FILES_INFO RequestId: {request_id}\t FilesCount: {files_count} files\t FilesSize: {files_size} bytes\t TransferDuration: {transfer_duration_ms} ms')

    ############################################

if __name__ == '__main__':
    lambda_handler(None, None)