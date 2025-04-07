import time
from denethor.core import denethor_logger as dlh
from denethor.utils import aws_utils as dau
import tree_constructor_core  as tcc
from denethor.utils import file_utils as dfu, utils as du

def handler(event, context):

    start_time = time.time()
    
    request_id = du.resolve_request_id(context)
    execution_tag = event.get('execution_tag')
    provider = event.get('provider')
    activity = event.get('activity')
    env_props = event.get('env_properties')
    
    logger = dlh.get_logger(execution_tag, provider, activity, env_props)
    logger.info(f'START RequestId: {request_id}\t Activity: {activity}\t Provider: {provider}')

    previous_activity = event.get('previous_activity')
    if previous_activity is None:
        input_files_props_sufix = 'input_files'
    else:
        input_files_props_sufix = previous_activity
    
    index_data = event.get('index_data')
    if index_data is None:
        input_files = event.get('input_data')
    else:
        input_files = event.get('input_data')[index_data]
    
    s3_bucket = env_props.get('bucket').get('name')
    s3_key_input  = env_props.get('bucket').get('key.' + input_files_props_sufix)
    s3_key_output = env_props.get('bucket').get('key.' + activity)
    
    # Format of the sequences: newick or nexus
    DATA_FORMAT = env_props.get(provider).get('data_format') 

    TMP_PATH = env_props.get(provider).get('path.tmp') # usado para escrever arquivos 'nopipe' durante o processo de validação
    INPUT_PATH = env_props.get(provider).get('path.' + input_files_props_sufix)
    OUTPUT_PATH = env_props.get(provider).get('path.' + activity)
    CLUSTALW_PATH = env_props.get(provider).get('path.clustalw')

    
    # Cleaning old temporary files and creating directories ##
    # dfu.remove_files(TMP_PATH)
    dfu.create_directory_if_not_exists(INPUT_PATH, OUTPUT_PATH, TMP_PATH)

    # Download input files ##
    dau.handle_consumed_files(request_id, provider, input_files, INPUT_PATH, s3_bucket, s3_key_input)

    # Building the tree file ##
    produced_files, duration_ms = tcc.tree_constructor(input_files, INPUT_PATH, TMP_PATH, OUTPUT_PATH, CLUSTALW_PATH, DATA_FORMAT)
    logger.info(f'TREE_CONSTRUCTOR RequestId: {request_id}\t Duration: {duration_ms} ms\t InputFile:{input_files}\t OutputFile:{produced_files}')
    
    # para evitar: 'PermissionError: [Errno 13] Permission denied' ao tentar abrir os arquivos logo após terem sido escritos
    time.sleep(0.100)
    
    # Upload output files ##
    dau.handle_produced_files(request_id, provider, produced_files, OUTPUT_PATH, s3_bucket, s3_key_output)
    
    end_time = time.time()
    func_duration_ms = (end_time - start_time) * 1000
    
    # "message": "END RequestId: 1c07a9af-e804-4d70-a287-54cde8ee7192\n",
    logger.info(f'END RequestId: {request_id}\t Activity: {activity}\t Provider: {provider}')

    # "message": "REPORT RequestId: 1c07a9af-e804-4d70-a287-54cde8ee7192\tDuration: 272.49 ms\tBilled Duration: 273 ms\tMemory Size: 2048 MB\tMax Memory Used: 111 MB\tInit Duration: 757.10 ms\t\n",
    logger.info(f'REPORT RequestId: {request_id}\t Duration: {func_duration_ms} ms\t Billed Duration: {int(func_duration_ms)} ms\t Memory Size: MB\t Max Memory Used: MB\t Init Duration: ms\t\n')

    
    return {
            "request_id" : request_id,
            "data" : produced_files
        }