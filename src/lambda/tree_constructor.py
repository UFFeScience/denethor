from denethor.utils.aws import aws_utils as dau
import tree_constructor_core  as tcc
from denethor.utils import file_utils as dfu, log_handler as dlh, utils as du

def handler(event, context):

    request_id = du.resolve_request_id(context)
    execution_id = event.get('execution_id')
    provider = event.get('provider')
    env_properties = event.get('env_properties')
    logger = dlh.get_logger(execution_id, 'tree_constructor', provider, env_properties)

    TMP_PATH = env_properties.get(provider).get('path.tmp') # usado para escrever arquivos 'nopipe' durante o processo de validação
    INPUT_PATH = env_properties.get(provider).get('path.input_file')
    OUTPUT_PATH = env_properties.get(provider).get('path.tree')
    CLUSTALW_PATH = env_properties.get(provider).get('path.clustalw')

    # formato das sequências: newick ou nexus
    DATA_FORMAT = env_properties.get(provider).get('data_format') 

    bucket_properties = event.get('bucket')
    s3_params = {
        'provider': provider,
        'bucket': bucket_properties.get('name'),
        'input_key': bucket_properties.get('key.input'),
        'output_key': bucket_properties.get('key.tree')
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