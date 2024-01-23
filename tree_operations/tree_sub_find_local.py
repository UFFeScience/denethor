from tree_sub_find_core import *
import boto3
import time
import timeit


# Substitua pelo caminho de entrada dos arquivos
PATH_BASE = 'tree_operations'
PATH_DATA = os.path.join(PATH_BASE, 'data')

# O bucket de entrada dos arquivos gerados pelo tree_constructor
# BUCKET_INPUT = 'mribeiro-bucket-output-tree'

# O bucket de saída dos arquivos gerados nesta etapa
# BUCKET_OUTPUT = 'mribeiro-bucket-output-subtree'
# S3_KEY_OUTPUT = ''

# Localização dos arquivos de entrada utilizados pela função
PATH_INPUT_LOCAL = os.path.join(PATH_DATA, 'output', 'trees') # na execução local é output do tree_constructor

# Localização dos arquivos gerados nesta etapa
PATH_OUTPUT_LOCAL = os.path.join(PATH_DATA, 'output', 'subtrees')

DATA_FORMAT = 'nexus' # newick ou nexus


def main():
    
    request_id = None

    print("******* Estado do ambiente de execução *******")
    print('pwd:', os.getcwd())

    #
    # ## Limpeza arquivos temporários ##
    #
    # remove_files(PATH_INPUT_LOCAL) #comentar na execução local
    remove_files(PATH_OUTPUT_LOCAL)

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
    print("Tempo de construção dos arquivos de subárvores:", subtree_time_ms, "milissegundos")
    
    total_file, total_file_size = get_num_files_and_size(PATH_OUTPUT_LOCAL)
    
    print(f"SUBTREE_FILES_CREATE RequestId: {request_id}\t TotalFiles: {total_file}\t TotalFileSize: {total_file_size} bytes\t Duration: {subtree_time_ms} ms")

    ###########
    
    
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

    ###########


if __name__ == '__main__':
    main()