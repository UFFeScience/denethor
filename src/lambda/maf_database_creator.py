from denethor.utils.aws import aws_utils as dau
import maf_database_creator_core as mdcc
from denethor.utils import file_utils as dfu, log_handler as dlh, utils as du

def handler(event, context):

    request_id = du.resolve_request_id(context)
    execution_id = event.get('execution_id')
    provider = event.get('provider')
    activity = event.get('activity')
    env_properties = event.get('env_properties')
    
    logger = dlh.get_logger(execution_id, provider, activity, env_properties)

    TMP_PATH = path_params.get('tmp') # usado para escrever arquivos 'nopipe' durante o processo de validação
    INPUT_PATH = path_params.get('subtree')
    OUTPUT_PATH = path_params.get('mafdb')

    # formato das sequências: newick ou nexus
    DATA_FORMAT = execution_env.get('data_format') 

    bucket_params = execution_env.get('bucket_params')
    s3_params = {
        'env_name': execution_env.get('env_name'),
        'bucket': bucket_params.get('bucket_name'),
        'input_key': bucket_params.get('key_subtree_files'),
        'output_key': bucket_params.get('key_mafdb_files')
    }
    
    # Cleaning old temporary files and creating directories ##
    # dfu.remove_files(TMP_PATH)
    dfu.create_directory_if_not_exists(INPUT_PATH, OUTPUT_PATH, TMP_PATH)
    
    # Get the input_file from the payload
    subtree_list = event.get('input_data')
    subtree_matrix = event.get('all_input_data')

    # Download input files ##
    dau.handle_consumed_files(request_id, subtree_matrix, INPUT_PATH, s3_params)

    # Criação do dicionário de similariadades de subárvore ##
    mafdb_file, maf_duration_ms = mdcc.maf_database_creator(subtree_list, subtree_matrix, INPUT_PATH, OUTPUT_PATH, DATA_FORMAT)
    logger.info(f'MAF_DATABASE_CREATOR RequestId: {request_id}\t Duration: {maf_duration_ms} ms\t InputSubtrees: {subtree_list}\t MafDatabaseFile: {mafdb_file}')
    
    # Upload output files ##
    dau.handle_produced_files(request_id, mafdb_file, OUTPUT_PATH, s3_params)

    return {
            "request_id" : request_id,
            "data" : mafdb_file
        }
        