import time
from denethor.utils.aws import aws_utils as dau
import subtree_constructor_core as smc
from denethor.utils import file_utils as dfu, log_handler as dlh, utils as du

def handler(event, context):

    request_id = du.resolve_request_id(context)
    execution_id = event.get('execution_id')
    provider = event.get('provider')
    activity = event.get('activity')
    env_props = event.get('env_properties')
    
    logger = dlh.get_logger(execution_id, provider, activity, env_props)

    TMP_PATH = env_props.get(provider).get('path.tmp') # usado para escrever arquivos 'nopipe' durante o processo de validação
    INPUT_PATH = env_props.get(provider).get('path.input_file')
    OUTPUT_PATH = env_props.get(provider).get('path.subtree')

    # formato das sequências: newick ou nexus
    DATA_FORMAT = env_props.get(provider).get('data_format') 

    bucket_props = event.get('bucket')
    s3_params = {
        'provider': provider,
        'bucket': bucket_props.get('name'),
        'input_key': bucket_props.get('key.input'),
        'output_key': bucket_props.get('key.tree')
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