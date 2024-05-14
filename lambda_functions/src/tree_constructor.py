import os
import environment as env
import tree_constructor_core  as tcc
import utils.denethor_utils as du
import utils.file_utils as fu

def handler(event, context):

    request_id = du.get_request_id(event, context)

    env_config = event.get('env_config')
    env_name = event.get('env_name')
    
    env.print_env(env_name, env_config)

    TMP_PATH = env_config.get('TMP_PATH') # usado para escrever arquivos 'nopipe' durante o processo de validação
    INPUT_PATH = env_config.get('INPUT_FILE_PATH')
    OUTPUT_PATH = env_config.get('TREE_PATH')
    CLUSTALW_PATH = env_config.get('CLUSTALW_PATH')
    
    # formato das sequências: newick ou nexus
    DATA_FORMAT = env_config.get('DATA_FORMAT') 

    ## Limpeza arquivos temporários (antigos) ##
    fu.remove_files(TMP_PATH)

    ## Criação de diretórios ##
    fu.create_directory_if_not_exists(INPUT_PATH, OUTPUT_PATH, TMP_PATH)

    # Get the input_file from the payload
    input_file = event.get('input_file')

    #
    ## Download do arquivo de entrada ##
    #
    du.handle_consumed_files(request_id, input_file, INPUT_PATH, event)


    #
    ## Construção do arquivo de árvore ##
    #
    print("Reading file %s" % input_file)
    produced_files, tree_duration_ms = tcc.tree_constructor(input_file, INPUT_PATH, TMP_PATH, OUTPUT_PATH, CLUSTALW_PATH, DATA_FORMAT)
    print(f'TREE_CONSTRUCTOR RequestId: {request_id}\t InputFile:{input_file} \t OutputTreeFile:{produced_files} \t Duration: {tree_duration_ms} ms')
    

    #
    ## Upload do(s) arquivo(s) de saída ##
    #
    du.handle_produced_files(request_id, produced_files, OUTPUT_PATH, event)
    
    return request_id, produced_files






# event = {
#     'execution_env': 'LOCAL_WIN',
#     'file': 'ORTHOMCL1'
# }


# handler(event, None)