import subtree_constructor_core as smc
from denethor_utils import file_utils as dfu, log_handler as dl, utils as du, aws_utils as dau

def handler(event, context):

    request_id = du.get_request_id(context)
    execution_env = du.get_execution_env(event)
    logger = dl.get_logger(execution_env)

    du.print_env_log(execution_env, logger)


    TMP_PATH = execution_env.get('tmp_path') # usado para escrever arquivos 'nopipe' durante o processo de validação
    INPUT_PATH = execution_env.get('subtree_path')
    
    # formato das sequências: newick ou nexus
    DATA_FORMAT = execution_env.get('data_format') 

    #
    ## Cleaning old temporary files and creating directories ##
    #
    dfu.remove_files(TMP_PATH)
    dfu.create_directory_if_not_exists(INPUT_PATH, TMP_PATH)
    
    #
    ## Get the input_file from the payload
    #
    subtree_list = event.get('input_data')
    subtree_matrix = event.get('all_input_data')

    #
    ## Download input files ##
    #
    params = {
        'env_name': execution_env.get('env_name'),
        'input_bucket': execution_env.get('bucket'),
        'input_key': execution_env.get('subtree_key_path')
    }
    dau.handle_consumed_files(request_id, subtree_matrix, INPUT_PATH, params)

    #
    ## Criação do dicionário de similariadades de subárvore ##
    #
    maf_database, max_maf, maf_duration_ms = smc.maf_database_create_2(subtree_list, subtree_matrix, INPUT_PATH, DATA_FORMAT)
    logger.info(f'MAF_DATABASE_CREATE RequestId: {request_id}\t InputSubtrees: {subtree_list}\t Duration: {maf_duration_ms} ms\t MaxMaf: {max_maf}\t MafDatabase: {maf_database}')
    
    #
    ## Upload output files ##
    #
    # dau.handle_produced_files(request_id, produced_files, OUTPUT_PATH, event)
    
    return {
            "request_id" : request_id,
            "produced_data" : maf_database
        }
        