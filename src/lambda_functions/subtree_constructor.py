import time
import subtree_constructor_core as smc
from denethor_utils import file_utils as dfu, log_handler as dlh, utils as du, aws_utils as dau

def handler(event, context):

    request_id = du.get_request_id(context)
    execution_id = du.get_execution_id(event)
    execution_env = du.get_execution_env(event)
    logger = dlh.get_logger(execution_id, 'subtree_constructor', execution_env)

    du.log_env_info(execution_env, logger)

    path_config = execution_env.get('path_config')
    TMP_PATH = path_config.get('tmp') # usado para escrever arquivos 'nopipe' durante o processo de validação
    INPUT_PATH = path_config.get('tree')
    OUTPUT_PATH = path_config.get('subtree')
    
    # formato das sequências: newick ou nexus
    DATA_FORMAT = execution_env.get('data_format') 

    bucket_config = execution_env.get('bucket_config')
    s3_params = {
        'env_name': execution_env.get('env_name'),
        'bucket': bucket_config.get('bucket_name'),
        'input_key': bucket_config.get('key_tree_files'),
        'output_key': bucket_config.get('key_subtree_files')
    }
    
    # Cleaning old temporary files and creating directories ##
    # dfu.remove_files(TMP_PATH)
    dfu.create_directory_if_not_exists(INPUT_PATH, OUTPUT_PATH, TMP_PATH)
    
    # Get the input_file from the payload
    input_files = event.get('input_data')

    # Download input files ##
    dau.handle_consumed_files(request_id, input_files, INPUT_PATH, s3_params)

    # Building the subtree files ##
    subtree_files, duration_ms = smc.subtree_constructor(input_files, INPUT_PATH, OUTPUT_PATH, DATA_FORMAT)
    logger.info(f'SUBTREE_CONSTRUCTOR RequestId: {request_id}\t Duration: {duration_ms} ms\t InputTree: {input_files}\t OutputSubtrees: {subtree_files}')

    # para evitar: 'PermissionError: [Errno 13] Permission denied' ao tentar abrir os arquivos logo após terem sido escritos
    time.sleep(0.100)

    # Upload output files ##
    dau.handle_produced_files(request_id, subtree_files, OUTPUT_PATH, s3_params)
    
    return {
            "request_id" : request_id,
            "data" : subtree_files
        }