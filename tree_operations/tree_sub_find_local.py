from tree_sub_find_core import *
import boto3
import time

# Substitua pelo caminho de entrada dos arquivos
PATH_BASE = 'tree_operations'
PATH_DATA = os.path.join(PATH_BASE, 'data')

# O bucket de entrada dos arquivos gerados pelo tree_constructor
# BUCKET_INPUT = 'mribeiro-bucket-output-tree'

# O bucket de saída dos arquivos gerados nesta etapa
# BUCKET_OUTPUT = 'mribeiro-bucket-output-subtree'

# Localização dos arquivos de entrada utilizados pela função
PATH_INPUT_LOCAL = os.path.join(PATH_DATA, 'output', 'trees')

# Localização dos arquivos gerados nesta etapa
PATH_OUTPUT_LOCAL = os.path.join(PATH_DATA, 'output', 'subtrees')

DATA_FORMAT = 'nexus' # newick ou nexus

def main():

    print("******* Estado do ambiente de execução *******")
    print('pwd:', os.getcwd())

    #
    # ## Limpeza arquivos temporários ##
    #
    remove_files(PATH_OUTPUT_LOCAL)
    # remove_files(PATH_INPUT_LOCAL) #comentar na execução local

    #
    # ## PERCORRER E MANIPULAR DIRETORIO ##
    # 

    # matriz com todas as subárvores
    subtree_matrix = []

    # Diretório de entrada de árvores
    files = os.listdir(PATH_INPUT_LOCAL)

    for file in files:
        print("Reading file %s" % file)     
        file_path = os.path.join(PATH_INPUT_LOCAL, file)
        
        subtree = sub_tree_constructor(file_path, file, PATH_OUTPUT_LOCAL, DATA_FORMAT)
        subtree_matrix.append(subtree)
    
    # para evitar: "PermissionError: [Errno 13] Permission denied" ao tentar abrir os arquivos logo após terem sido escritos
    time.sleep(0.100)

    subtree_matrix = fill_matrix(subtree_matrix, value=None)

    dict_maf_database, max_maf = create_maf_database(subtree_matrix, PATH_OUTPUT_LOCAL, DATA_FORMAT)

    print('max_maf:', max_maf)
    print('Final dict_maf_database:', dict_maf_database)

    
if __name__ == '__main__':
    main()