import maf_database_creator_core as mdcc
from denethor_utils import file_utils as dfu, log_handler as dlh, utils as du, aws_utils as dau

def handler(event, context):

    request_id = du.get_request_id(context)
    execution_id = du.get_execution_id(event)
    execution_env = du.get_execution_env(event)
    logger = dlh.get_logger(execution_id, execution_env)

    du.log_env_info(execution_env, logger)

    path_config = execution_env.get('path_config')
    TMP_PATH = path_config.get('tmp') # usado para escrever arquivos 'nopipe' durante o processo de validação
    INPUT_PATH = path_config.get('subtree')
    
    # formato das sequências: newick ou nexus
    DATA_FORMAT = execution_env.get('data_format') 

    bucket_config = execution_env.get('bucket_config')
    s3_params = {
        'env_name': execution_env.get('env_name'),
        'bucket': bucket_config.get('bucket_name'),
        'input_key': bucket_config.get('key_subtree_files'),
        'output_key': ""
    }
    
    # Cleaning old temporary files and creating directories ##
    dfu.remove_files(TMP_PATH)
    dfu.create_directory_if_not_exists(INPUT_PATH, TMP_PATH)
    
    # Get the input_file from the payload
    subtree_list = event.get('input_data')
    subtree_matrix = event.get('all_input_data')

    # Download input files ##
    dau.handle_consumed_files(request_id, subtree_matrix, INPUT_PATH, s3_params)

    # Criação do dicionário de similariadades de subárvore ##
    maf_database, max_maf, maf_duration_ms = mdcc.maf_database_create(subtree_list, subtree_matrix, INPUT_PATH, DATA_FORMAT)
    logger.info(f'MAF_DATABASE_CREATE RequestId: {request_id}\t Duration: {maf_duration_ms} ms\t InputSubtrees: {subtree_list}\t MaxMaf: {max_maf}\t MafDatabase: {maf_database}')
    
    return {
            "request_id" : request_id,
            "data" : maf_database
        }
        