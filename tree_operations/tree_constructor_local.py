from tree_constructor_core import *
import timeit

# # O bucket e key de saída dos arquivos gerados nesta etapa
# BUCKET_OUTPUT = 'mribeiro-bucket-output-tree'
# S3_KEY_OUTPUT = ''

# Localização dos arquivos de entrada utilizados pela função
PATH_INPUT = 'tree_operations\\data\\full_dataset' # testset ou full_dataset

# Localização dos arquivos gerados nesta etapa
PATH_OUTPUT = 'tree_operations\\data\\output\\trees'

# Usado para escrever arquivos 'nopipe' durante o processo de validação
PATH_TMP = 'tree_operations\\data\\tmp'

# Localização do binário do Clustalw
PATH_CLUSTALW = 'tree_operations\\lib\\opt\\python\ClustalW2'

# Formato das sequências
DATA_FORMAT = 'nexus' # newick ou nexus

def lambda_handler(event, context):

    request_id = None
    
    print("Estado do ambiente de execução")
    print('pwd:', os.getcwd())
    
    #
    # ## Limpeza arquivos antigos ##
    #
    remove_files(PATH_TMP)
    remove_files(PATH_OUTPUT)

    #
    # ## PERCORRER E MANIPULAR DIRETORIO ##
    # 
    # listagem de arquivos
    files = os.listdir(PATH_INPUT)
    
    #
    # ## Construção dos arquivos de árvores ##
    # 
    start_time = timeit.default_timer()

    for name_file in files:
        print("Reading file %s" % name_file)
        tree_constructor(name_file, PATH_INPUT, PATH_TMP, PATH_OUTPUT, PATH_CLUSTALW, DATA_FORMAT)

    end_time = timeit.default_timer()
    tree_time_ms = (end_time - start_time) * 1000
    
    print(f"TREE_CONSTRUCTOR RequestId: {request_id}\t Duration: {tree_time_ms} ms")

    ############################################
   
if __name__ == '__main__':
    lambda_handler(None, None)
