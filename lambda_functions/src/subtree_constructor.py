import subtree_mining_core as smc
import utils.denethor_utils as du
import utils.file_utils as fu

def handler(event, context):

    request_id = du.get_request_id(context)
    execution_env = du.get_execution_env(event)
    
    du.print_env(execution_env)

    TMP_PATH = execution_env.get('TMP_PATH') # usado para escrever arquivos 'nopipe' durante o processo de validação
    INPUT_PATH = execution_env.get('TREE_PATH')
    OUTPUT_PATH = execution_env.get('SUBTREE_PATH')
    
    # formato das sequências: newick ou nexus
    DATA_FORMAT = execution_env.get('DATA_FORMAT') 

    #
    ## Cleaning old temporary files and creating directories ##
    #
    fu.remove_files(TMP_PATH)
    fu.create_directory_if_not_exists(INPUT_PATH, OUTPUT_PATH, TMP_PATH)
    
    #
    ## Get the input_file from the payload
    #
    input_files = event.get('input_data')

    #
    ## Download input files ##
    #
    du.handle_consumed_files(request_id, input_files, INPUT_PATH, event)

    #
    ## Building the subtree files ##
    #
    # subtree_matrix = []
    produced_files, duration_ms = smc.subtree_constructor(input_files, INPUT_PATH, OUTPUT_PATH, DATA_FORMAT)
    # subtree_matrix.append(produced_files)
    print(f'SUBTREE_CONSTRUCTOR RequestId: {request_id}\t InputTree: {input_files}\t OutputSubtrees: {produced_files}\t Duration: {duration_ms} ms')

    #
    ## Upload output files ##
    #
    du.handle_produced_files(request_id, produced_files, OUTPUT_PATH, event)
    
    return {
            "request_id" : request_id,
            "input_data" : input_files,
            "produced_data" : produced_files
        }


