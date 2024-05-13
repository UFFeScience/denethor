import os
import environment as env
import file_utils as file_utils
import subtree_mining_core as smc

def handler(event, context):

    if context is None:
        request_id = event.get('request_id', '0')
    else:
        request_id = context.aws_request_id

    env_conf = event['env_conf']
    env_name = event['env_name']
    env.print_env(env_name, env_conf)

    TMP_PATH = env_conf.get('TMP_PATH') # usado para escrever arquivos 'nopipe' durante o processo de validação
    INPUT_PATH = env_conf.get('TREE_PATH')
    OUTPUT_PATH = env_conf.get('SUBTREE_PATH')
    
    # formato das sequências: newick ou nexus
    DATA_FORMAT = env_conf.get('DATA_FORMAT') 

    ## Limpeza arquivos temporários (antigos) ##
    file_utils.remove_files(TMP_PATH)

    ## Criação de diretórios ##
    file_utils.create_directory_if_not_exists(TMP_PATH)
    file_utils.create_directory_if_not_exists(INPUT_PATH)
    file_utils.create_directory_if_not_exists(OUTPUT_PATH)
    
    # Get the input_file from the payload
    input_file = event['file']



    #
    ## Download do arquivo de entrada ##
    #
    download_time_ms = None
    if env_name == 'LAMBDA':
        # Get the input_bucket from the payload
        input_bucket = event['inputBucket']
        input_key = event['inputKey']
        # Download file from s3 bucket into lambda function
        download_time_ms = file_utils.download_and_log_single_file_from_s3_new(request_id, input_bucket, input_key, input_file, INPUT_PATH)
        
    f_info = file_utils.get_files_info(input_file, INPUT_PATH)      
    print(f'CONSUMED_FILES_INFO RequestId: {request_id}\t FilesCount: {f_info['files_count']} files\t FilesSize: {f_info['files_size']} bytes\t TransferDuration: {download_time_ms} ms\t ConsumedFiles: {input_file}')

    ##################


    
    subtree_matrix = []
    #
    ## Criação do dicionário de similariadades de subárvore ##
    #
    start_time = timeit.default_timer()
    dict_maf_database, max_maf, duration = smc.maf_database_create(subtree_matrix, OUTPUT_PATH, DATA_FORMAT)
    end_time = timeit.default_timer()
    maf_time_ms = (end_time - start_time) * 1000

    print(f'MAF_DATABASE_CREATE RequestId: {request_id}\t MaxMaf: {max_maf}\t Duration: {maf_time_ms} ms\t MafDatabase: {dict_maf_database}')

    ##################
    
    
    #
    ## Upload do(s) arquivo(s) de saída ##
    #
    upload_duration_ms = None
    if env_name == 'LAMBDA':
        ## Copy tree file to S3 ##
        output_bucket = event.get('outputBucket')
        output_key = event.get('outputKey')
        
        # Upload files from lambda function into s3
        upload_duration_ms = file_utils.upload_to_s3(request_id, output_bucket, output_key, produced_files, OUTPUT_PATH)
        
    ##################    

    
    f_info = file_utils.get_files_info(produced_files, OUTPUT_PATH)      
    print(f'PRODUCED_FILES_INFO RequestId: {request_id}\t FilesCount: {f_info['files_count']} files\t FilesSize: {f_info['files_size']} bytes\t TransferDuration: {upload_duration_ms} ms\t ProducedFiles: {produced_files}')
    
    
    return request_id, produced_files


