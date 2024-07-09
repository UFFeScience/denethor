import time
import subtree_mining_core as smc
from utils import file_utils as fu
from denethor.src.utils import denethor_logger as dl, denethor_utils as du, denethor_aws_utils as dau


def handler(event, context):

    request_id = du.get_request_id(context)
    execution_env = du.get_execution_env(event)
    logger = dl.get_logger(execution_env)

    du.print_env(execution_env)
    du.print_env_to_log(execution_env, logger)

    TMP_PATH = execution_env.get('tmp_path') # usado para escrever arquivos 'nopipe' durante o processo de validação
    INPUT_PATH = execution_env.get('tree_path')
    OUTPUT_PATH = execution_env.get('subtree_path')
    
    # formato das sequências: newick ou nexus
    DATA_FORMAT = execution_env.get('data_format') 

    #
    ## Cleaning old temporary files and creating directories ##
    #
    fu.remove_files(TMP_PATH)
    fu.create_directory_if_not_exists(INPUT_PATH, OUTPUT_PATH, TMP_PATH)
    
    #
    ## Get the input_file from the payload
    #
    input_files = event.get('input_data')

    #
    ## Download input files ##
    #
    params = {
        'env_name': execution_env.get('env_name'),
        'input_bucket': execution_env.get('bucket'),
        'input_key': execution_env.get('tree_key_path')
    }
    dau.handle_consumed_files(request_id, input_files, INPUT_PATH, event)

    #
    ## Building the subtree files ##
    #
    # subtree_matrix = []
    produced_files, duration_ms = smc.subtree_constructor(input_files, INPUT_PATH, OUTPUT_PATH, DATA_FORMAT)
    # subtree_matrix.append(produced_files)
    print(f'SUBTREE_CONSTRUCTOR RequestId: {request_id}\t InputTree: {input_files}\t OutputSubtrees: {produced_files}\t Duration: {duration_ms} ms')
    logger.info(f'SUBTREE_CONSTRUCTOR RequestId: {request_id}\t InputTree: {input_files}\t OutputSubtrees: {produced_files}\t Duration: {duration_ms} ms')

    # para evitar: 'PermissionError: [Errno 13] Permission denied' ao tentar abrir os arquivos logo após terem sido escritos
    time.sleep(0.100)

    #
    ## Upload output files ##
    #
    params = {
        'env_name': execution_env.get('env_name'),
        'output_bucket': execution_env.get('bucket'),
        'output_key': execution_env.get('subtree_key_path')
    }
    dau.handle_produced_files(request_id, produced_files, OUTPUT_PATH, event)
    
    return {
            "request_id" : request_id,
            "produced_data" : produced_files
        }