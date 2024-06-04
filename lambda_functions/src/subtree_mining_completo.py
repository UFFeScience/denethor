import os
import time
import timeit
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
    file_utils.create_directory_if_not_exists(INPUT_PATH, OUTPUT_PATH, TMP_PATH)
    
    # Get the input_file from the payload
    # input_file = event['file']
    input_files = event['files']

    ############################### Download das árvores ##############################
    download_duration_ms = None
    if env_name == 'LAMBDA':
        # Get the input_bucket from the payload
        input_bucket = event['input_bucket']
        ## Download multiple files from s3 bucket into lambda function
        download_duration_ms = smc.download_and_log_multiple_files_from_s3(request_id, input_bucket, INPUT_PATH, input_files, DATA_FORMAT)
    ###################################################################################


    # TODO: ajustar essas variáveis pois na execução local teremos arquivos de execuções anteriores
    files_count, files_size = file_utils.get_num_files_and_size(INPUT_PATH)
    print(f'CONSUMED_FILES_INFO RequestId: {request_id}\t FilesCount: {files_count} files\t FilesSize: {files_size} bytes\t TransferDuration: {download_duration_ms} ms\t ConsumedFiles: {input_files}')


    
    ###################### Construção dos arquivos de subárvores ######################
    total_subtree_duration_ms = 0
    subtree_matrix = []
    for tree_file in os.listdir(INPUT_PATH):
        subtree, subtree_duration_ms = smc.subtree_constructor(tree_file, INPUT_PATH, OUTPUT_PATH, DATA_FORMAT)
        subtree_matrix.append(subtree)
        total_subtree_duration_ms += subtree_duration_ms

    print(f'SUBTREE_CONSTRUCTOR RequestId: {request_id}\t Duration: {total_subtree_duration_ms} ms')
    ###################################################################################
    
    
    # para evitar: 'PermissionError: [Errno 13] Permission denied' ao tentar abrir os arquivos logo após terem sido escritos
    time.sleep(0.100)

    
    ############## Criação do dicionário de similariadades de subárvore ##############
    start_time = timeit.default_timer()
    dict_maf_database, max_maf = smc.maf_database_create(subtree_matrix, OUTPUT_PATH, DATA_FORMAT)
    end_time = timeit.default_timer()
    maf_time_ms = (end_time - start_time) * 1000
    
    print(f'MAF_DATABASE_CREATE RequestId: {request_id}\t MaxMaf: {max_maf}\t Duration: {maf_time_ms} ms\t MafDatabase: {dict_maf_database}')
    ###################################################################################


    
    ############################## Upload das subárvores ##############################
    upload_duration_ms = None
    if env_name == 'LAMBDA':
        ## Copy tree file to S3 ##
        output_bucket = event.get('output_bucket')
        output_key = event.get('output_key')
        # Upload files from lambda function into s3
        upload_duration_ms = smc.upload_and_log_multiple_files_to_s3(request_id, output_bucket, output_key, OUTPUT_PATH, produced_files)
    ###################################################################################
    

    # TODO: ajustar essas variáveis pois na execução local teremos arquivos de execuções anteriores
    produced_files = os.listdir(OUTPUT_PATH)
    files_count, files_size = file_utils.get_num_files_and_size(OUTPUT_PATH)
    
    print(f'PRODUCED_FILES_INFO RequestId: {request_id}\t FilesCount: {files_count} files\t FilesSize: {files_size} bytes\t TransferDuration: {upload_duration_ms} ms\t ProducedFiles: {produced_files}')

    
    
    return request_id


