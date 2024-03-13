from datetime import datetime
from subtree_mining_core import *
from file_utils import *

INPUT_PATH = 'lambda_functions/data/trees' # na execução local é output do tree_constructor
OUTPUT_PATH = 'lambda_functions/data/subtrees'
DATA_FORMAT = 'nexus' # Formato das sequências: newick ou nexus

request_id = None

print('******* Estado do ambiente de execução *******')
print(f'Start time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print('pwd:', os.getcwd())
print('INPUT_PATH:', os.listdir(INPUT_PATH))
print('OUTPUT_PATH:', os.listdir(OUTPUT_PATH))
print('DATA_FORMAT:', DATA_FORMAT)

## Limpeza arquivos temporários ##
remove_files(OUTPUT_PATH)

## Construção dos arquivos de subárvores ##
start_time = timeit.default_timer()
total_subtree_duration_ms = 0
subtree_matrix = []
for tree_file in os.listdir(INPUT_PATH):
    subtree, subtree_duration_ms = subtree_constructor(tree_file, INPUT_PATH, OUTPUT_PATH, DATA_FORMAT)
    subtree_matrix.append(subtree)
    total_subtree_duration_ms += subtree_duration_ms

print(f'SUBTREE_CONSTRUCTOR RequestId: {request_id}\t Duration: {total_subtree_duration_ms} ms')

############################################

# para evitar: 'PermissionError: [Errno 13] Permission denied' ao tentar abrir os arquivos logo após terem sido escritos
time.sleep(0.100)

## Criação do dicionário de similariadades de subárvore ##
start_time = timeit.default_timer()
dict_maf_database, max_maf = maf_database_create(subtree_matrix, OUTPUT_PATH, DATA_FORMAT)
end_time = timeit.default_timer()
maf_time_ms = (end_time - start_time) * 1000

print(f'MAF_DATABASE_CREATE RequestId: {request_id}\t MaxMaf: {max_maf}\t Duration: {maf_time_ms} ms\t MafDatabase: {dict_maf_database}')

############################################

transfer_duration_ms = None
files_count, files_size = get_num_files_and_size(OUTPUT_PATH)
print(f'PRODUCED_FILES_INFO RequestId: {request_id}\t FilesCount: {files_count} files\t FilesSize: {files_size} bytes\t TransferDuration: {transfer_duration_ms} ms')
