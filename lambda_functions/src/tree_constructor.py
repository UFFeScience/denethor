from environment import Environment
from tree_constructor_core import *
import file_utils

def handler(event, context):

    if context is None:
        request_id = None
    else:
        request_id = context.aws_request_id

    env = Environment(event)
    env.print()

    TMP_PATH = env.TMP_PATH # usado para escrever arquivos 'nopipe' durante o processo de validação
    INPUT_PATH = env.DATASET_PATH
    OUTPUT_PATH = env.TREE_PATH 
    CLUSTALW_PATH = env.CLUSTALW_PATH
    
    # formato das sequências: newick ou nexus
    DATA_FORMAT = env.DATA_FORMAT 

    ## Limpeza arquivos antigos ##
    file_utils.remove_files(TMP_PATH)

    ## Criação de diretórios ##
    file_utils.create_directory_if_not_exists(TMP_PATH)
    file_utils.create_directory_if_not_exists(INPUT_PATH)
    file_utils.create_directory_if_not_exists(OUTPUT_PATH)

    # Get the input_file from the payload
    input_file = event['file']

    ############################################
    if env == 'LAMBDA':
        # Get the input_bucket from the payload
        input_bucket = event['inputBucket']

        # Download file from s3 bucket into lambda function
        down_info = download_and_log_single_file_from_s3_new(request_id, input_bucket, input_file, INPUT_PATH)
        
        print(f'CONSUMED_FILES_INFO RequestId: {request_id}\t FilesCount: {down_info['file_count']} files\t FilesSize: {down_info['file_size']} bytes\t TransferDuration: {down_info['download_time_ms']} ms\t ConsumedFiles: {input_file}')
    ############################################

    ############################################
    #
    # ## Construção do arquivo de árvore ##
    #
    print("Reading file %s" % input_file)
    tree_file, tree_duration_ms = tree_constructor(input_file, INPUT_PATH, TMP_PATH, OUTPUT_PATH, CLUSTALW_PATH, DATA_FORMAT)
    print(f'TREE_CONSTRUCTOR RequestId: {request_id}\t InputFile:{input_file} \t OutputTreeFile:{tree_file} \t Duration: {tree_duration_ms} ms')
    ############################################

    ############################################
    if env == 'LAMBDA':
        ## Copy tree file to S3 ##
        output_bucket = event['outputBucket']
        output_key = event['outputKey']
        
        # Upload files from lambda function into s3
        up_info = upload_and_log_single_file_to_s3(request_id, output_bucket, output_key, OUTPUT_PATH, tree_file)
        
        print(f'PRODUCED_FILES_INFO RequestId: {request_id}\t FilesCount: {up_info['file_count']} files\t FilesSize: {up_info['file_size']} bytes\t TransferDuration: {up_info['upload_duration_ms']} ms\t ProducedFiles: {tree_file}')
    ############################################    
        
    return "OK"
