from datetime import datetime
from tree_constructor_core import *
from file_utils import *

TMP_PATH = 'lambda_functions/data/tmp' # Usado para escrever arquivos 'nopipe' durante o processo de validação
INPUT_PATH = 'data/testset' # testset ou full_dataset
OUTPUT_PATH = 'lambda_functions/data/trees'
CLUSTALW_PATH = 'lambda_functions/lib/opt/python/ClustalW2' # Windows
#CLUSTALW_PATH = 'lambda_functions/lib/opt/python/clustalw-2.1-linux-x86_64-libcppstatic' # Linux

DATA_FORMAT = 'nexus' # Formato das sequências: newick ou nexus

request_id = None

print("******* Estado do ambiente de execução *******")
print(f'Start time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print('pwd:', os.getcwd())
print('TMP_PATH:', os.listdir(TMP_PATH))
print('INPUT_PATH:', os.listdir(INPUT_PATH))
print('OUTPUT_PATH:', os.listdir(OUTPUT_PATH))
print('CLUSTALW_PATH:', os.listdir(CLUSTALW_PATH))
print('DATA_FORMAT:', DATA_FORMAT)

## Limpeza arquivos antigos ##
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
