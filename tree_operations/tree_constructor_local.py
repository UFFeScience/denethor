from tree_constructor_core import *
from datetime import datetime


TMP_PATH = 'tree_operations/data/executions/tmp' # Usado para escrever arquivos 'nopipe' durante o processo de validação

INPUT_PATH = 'tree_operations/data/testset' # testset ou full_dataset

OUTPUT_PATH = 'tree_operations/data/executions/trees'

CLUSTALW_PATH = 'tree_operations/lib/opt/python/ClustalW2' # Windows
#CLUSTALW_PATH = 'tree_operations/lib/opt/python/clustalw-2.1-linux-x86_64-libcppstatic' # Linux

DATA_FORMAT = 'nexus' # Formato das sequências: newick ou nexus


def handler(event, context):

    request_id = None
    
    print("******* Estado do ambiente de execução *******")
    print(f'Start time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('pwd:', os.getcwd())
    
    #
    # ## Limpeza arquivos antigos ##
    #
    remove_files(TMP_PATH)
    remove_files(OUTPUT_PATH)

    #
    # ## Construção dos arquivos de árvores ##
    #
    files = os.listdir(INPUT_PATH) # listagem de arquivos
    total_tree_duration_ms = 0
    for input_file in files:
        print("Reading file %s" % input_file)
        tree_duration_ms = tree_constructor(input_file, INPUT_PATH, TMP_PATH, OUTPUT_PATH, CLUSTALW_PATH, DATA_FORMAT)
        total_tree_duration_ms += tree_duration_ms
        print(f'TREE_CONSTRUCTOR RequestId: {request_id}\t File:{input_file}\t Duration: {tree_duration_ms} ms')

    print(f'TREE_CONSTRUCTOR RequestId: {request_id}\t TotalDuration: {total_tree_duration_ms} ms')

    ############################################

    return "OK"

   
if __name__ == '__main__':
    handler(None, None)
