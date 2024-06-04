import tree_constructor_core  as tcc
import utils.denethor_utils as du
import utils.file_utils as fu

def handler(event, context):

    request_id = du.get_request_id(context)
    execution_env = du.get_execution_env(event)
    
    du.print_env(execution_env)

    TMP_PATH = execution_env.get('TMP_PATH') # usado para escrever arquivos 'nopipe' durante o processo de validação
    INPUT_PATH = execution_env.get('INPUT_FILE_PATH')
    OUTPUT_PATH = execution_env.get('TREE_PATH')
    CLUSTALW_PATH = execution_env.get('CLUSTALW_PATH')

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
    ## Building the tree file ##
    #
    produced_files, duration_ms = tcc.tree_constructor(input_files, INPUT_PATH, TMP_PATH, OUTPUT_PATH, CLUSTALW_PATH, DATA_FORMAT)
    print(f'TREE_CONSTRUCTOR RequestId: {request_id}\t InputFile:{input_files} \t OutputTreeFile:{produced_files} \t Duration: {duration_ms} ms')

    #
    ## Upload output files ##
    #
    du.handle_produced_files(request_id, produced_files, OUTPUT_PATH, event)
    
    return {
            "request_id" : request_id,
            "input_data" : input_files,
            "produced_data" : produced_files
        }




# event = {
#     'execution_env': 'local_win',
#     'file': 'ORTHOMCL1'
# }


# handler(event, None)