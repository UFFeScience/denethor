import subtree_mining_core as smc
from utils import file_utils as fu
from denethor.src.utils import denethor_logger as dl
from denethor.src.utils import denethor_utils as du

def handler(event, context):

    request_id = du.get_request_id(context)
    execution_env = du.get_execution_env(event)
    logger = dl.get_logger(execution_env)

    du.print_env(execution_env)
    du.print_env_to_log(execution_env, logger)

    TMP_PATH = execution_env.get('tmp_path') # usado para escrever arquivos 'nopipe' durante o processo de validação
    INPUT_PATH = execution_env.get('subtree_path')
    
    # formato das sequências: newick ou nexus
    DATA_FORMAT = execution_env.get('data_format') 

    #
    ## Cleaning old temporary files and creating directories ##
    #
    fu.remove_files(TMP_PATH)
    fu.create_directory_if_not_exists(INPUT_PATH, TMP_PATH)
    
    #
    ## Get the input_file from the payload
    #
    input_files = event.get('input_data')
    subtree_matrix = event.get('all_input_data')

    #
    ## Download input files ##
    #
    du.handle_consumed_files(request_id, input_files, INPUT_PATH, event)

    #
    ## Criação do dicionário de similariadades de subárvore ##
    #
    maf_database = None
    max_maf = 0
    
    # verificando se input_file é uma lista de arquivos
    if isinstance(input_files, list):
        subtree_list = input_files
        maf_database, max_maf, maf_duration_ms = smc.maf_database_create_2(subtree_list, subtree_matrix, maf_database, max_maf, INPUT_PATH, DATA_FORMAT)
        print(f'MAF_DATABASE_CREATE RequestId: {request_id}\t InputSubtrees: {input_files}\t Duration: {maf_duration_ms} ms\t MaxMaf: {max_maf}\t MafDatabase: {maf_database}')
        logger.info(f'MAF_DATABASE_CREATE RequestId: {request_id}\t InputSubtrees: {input_files}\t Duration: {maf_duration_ms} ms\t MaxMaf: {max_maf}\t MafDatabase: {maf_database}')
    else:
        # input_file é um arquivo
        raise ValueError(f'MAF_DATABASE_CREATE: Invalid input_file: {input_files}. List of files expected.')

    #
    ## Upload output files ##
    #
    # du.handle_produced_files(request_id, produced_files, OUTPUT_PATH, event)
    
    return {
            "request_id" : request_id,
            "produced_data" : maf_database
        }
        

