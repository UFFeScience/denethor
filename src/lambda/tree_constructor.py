from denethor.utils.aws import aws_utils as dau
import tree_constructor_core  as tcc
from denethor.utils import file_utils as dfu, log_handler as dlh, utils as du

def handler(event, context):

    request_id = du.get_request_id(context)
    execution_id = du.get_execution_id(event)
    execution_env = du.get_execution_env(event)
    logger = dlh.get_logger(execution_id, 'tree_constructor', execution_env)

    du.log_env_info(execution_env, logger)
    path_params = execution_env.get('path_params')
    TMP_PATH = path_params.get('tmp') # usado para escrever arquivos 'nopipe' durante o processo de validação
    INPUT_PATH = path_params.get('input_file')
    OUTPUT_PATH = path_params.get('tree')
    CLUSTALW_PATH = path_params.get('clustalw')

    # formato das sequências: newick ou nexus
    DATA_FORMAT = execution_env.get('data_format') 

    bucket_params = execution_env.get('bucket_params')
    s3_params = {
        'env_name': execution_env.get('env_name'),
        'bucket': bucket_params.get('bucket_name'),
        'input_key': bucket_params.get('key_input_files'),
        'output_key': bucket_params.get('key_tree_files')
    }
    
    # Cleaning old temporary files and creating directories ##
    # dfu.remove_files(TMP_PATH)
    dfu.create_directory_if_not_exists(INPUT_PATH, OUTPUT_PATH, TMP_PATH)

    # Get the input_file from the payload
    input_files = event.get('input_data')

    # Download input files ##
    dau.handle_consumed_files(request_id, input_files, INPUT_PATH, s3_params)

    # Building the tree file ##
    tree_files, duration_ms = tcc.tree_constructor(input_files, INPUT_PATH, TMP_PATH, OUTPUT_PATH, CLUSTALW_PATH, DATA_FORMAT)
    logger.info(f'TREE_CONSTRUCTOR RequestId: {request_id}\t Duration: {duration_ms} ms\t InputFile:{input_files}\t OutputFile:{tree_files}')

    # Upload output files ##
    dau.handle_produced_files(request_id, tree_files, OUTPUT_PATH, s3_params)
    
    return {
            "request_id" : request_id,
            "data" : tree_files
        }