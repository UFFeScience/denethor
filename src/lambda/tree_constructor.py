import time
from denethor.utils.aws import aws_utils as dau
import tree_constructor_core  as tcc
from denethor.utils import file_utils as dfu, log_handler as dlh, utils as du

def handler(event, context):

    request_id = du.resolve_request_id(context)
    execution_id = event.get('execution_id')
    provider = event.get('provider')
    activity = event.get('activity')
    input_files = event.get('input_data')
    
    env_props = event.get('env_properties')
    s3_bucket = env_props.get('bucket').get('name')
    s3_key_input  = env_props.get('bucket').get('key.input')
    s3_key_output = env_props.get('bucket').get('key.tree')
    
    # Format of the sequences: newick or nexus
    DATA_FORMAT = env_props.get(provider).get('data_format') 

    TMP_PATH = env_props.get(provider).get('path.tmp') # usado para escrever arquivos 'nopipe' durante o processo de validação
    INPUT_PATH = env_props.get(provider).get('path.input')
    OUTPUT_PATH = env_props.get(provider).get('path.tree')
    CLUSTALW_PATH = env_props.get(provider).get('path.clustalw')

    logger = dlh.get_logger(execution_id, provider, activity, env_props)
    
    # Cleaning old temporary files and creating directories ##
    # dfu.remove_files(TMP_PATH)
    dfu.create_directory_if_not_exists(INPUT_PATH, OUTPUT_PATH, TMP_PATH)

    # Download input files ##
    dau.handle_consumed_files(request_id, provider, input_files, INPUT_PATH, s3_bucket, s3_key_input)

    # Building the tree file ##
    tree_files, duration_ms = tcc.tree_constructor(input_files, INPUT_PATH, TMP_PATH, OUTPUT_PATH, CLUSTALW_PATH, DATA_FORMAT)
    logger.info(f'TREE_CONSTRUCTOR RequestId: {request_id}\t Duration: {duration_ms} ms\t InputFile:{input_files}\t OutputFile:{tree_files}')
    
    # para evitar: 'PermissionError: [Errno 13] Permission denied' ao tentar abrir os arquivos logo após terem sido escritos
    time.sleep(0.100)
    
    # Upload output files ##
    dau.handle_produced_files(request_id, provider, tree_files, OUTPUT_PATH, s3_bucket, s3_key_output)
    
    return {
            "request_id" : request_id,
            "data" : tree_files
        }