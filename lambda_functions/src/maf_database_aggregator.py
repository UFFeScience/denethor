import subtree_mining_core as smc
import utils.denethor_utils as du
import utils.file_utils as fu

def handler(event, context):

    request_id = du.get_request_id(context)
    execution_env = du.get_execution_env(event)
    
    du.print_env(execution_env)

    #
    ## Get the input_file from the payload
    #
    input_data = event.get('input_data')
    # input_data contem uma lista de maf_databases parciais
    # gerados comparando cada grupo de subárvores com todas as outras
    # cada maf_database parcial contem um dicionário de similaridades de subárvores 
    # onde o valor do id indica o grau de similaridade
    # A ideia é unir os maf_databases parciais em um único maf_database levando em conta esse grau de similaridade

    i = 0
    for partial_maf_database in input_data:
        print(f"___________  {i}  _______________")
        for k,v in partial_maf_database.items():
            print(f'Partial MAF_DATABASE: {k} {v}')
        print("_______________________________")
        i += 1


    maf_database = {}






    #
    ## Criação do dicionário de similariadades de subárvore ##
    #
    maf_database = None
    max_maf = 0
    
    maf_database = {}
    max_maf = 0
    for k,v in maf_database.items():
        max_maf = max(max_maf, k)
    
    
    
    
    
    
    
    #
    ## Upload output files ##
    #
    # du.handle_produced_files(request_id, produced_files, OUTPUT_PATH, event)
    
    return {
            "request_id" : request_id,
            "input_data" : input_files,
            "maf_database" : maf_database,
            "max_maf" : max_maf
        }
        

