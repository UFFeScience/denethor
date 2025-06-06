import math, os, time, timeit, json
from denethor.core import denethor_logger as dlh
from denethor.utils import aws_utils as dau
import maf_database_creator_core as mdcc
from denethor.utils import file_utils as dfu, utils as du

def handler(event, context):

    function_start_time = timeit.default_timer()
    
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
    dau.handle_consumed_files(request_id, provider, input_files, INPUT_PATH, s3_bucket, s3_key_input, logger)



    # Get the input_data from the payload
    
    # input_data contem uma lista de instâncias de maf_databases
    # gerados comparando cada grupo de subárvores com todas as outras
    # cada instância de maf_database contem:
    # 1) id: grau de similaridade
    # 2) chave: nome do arquivo de subárvores
    # 3) valor: lista de subárvores que são similares
    # A ideia é unir os maf_databases parciais em um único maf_database levando em conta o grau de similaridade
    
    # Exemplo de 'input_data' para os 5 primeiros datasets.
    #
    # -> conjunto de dados (n1):
    #   * lista contendo o resultado de cada ativação de comparação de subárvores
    #   * n1 = (0,3,4) estão vazios, pois não houve similiaridade entre a subarvores analisadas na ativação e todas as demais (grau = 0)
    #   * n1 = (1,2) contém dados de subárvores similares
    #
    # -> conjunto de dados (n2):
    #   * é cada item da lista (n1)
    #   * tipo de dados: dicionário
    #   * chave: o grau de similiaridade | valor: um dicionário de similaridades daquele grau
    #
    #  -> conjunto de dados (n3):
    #    * é cada item valor de (n2)
    #    * tipo de dados: dicionário
    #    * chave: nome da subarvore | valor: lista de subárvores similares
    #
    # 0: {}
    # 1: {
    #     1: {'tree_ORTHOMCL256_Inner4.nexus': ['tree_ORTHOMCL256_2_Inner4.nexus', 'tree_ORTHOMCL256_2_Inner5.nexus', 'tree_ORTHOMCL256_2_Inner6.nexus', 'tree_ORTHOMCL256_2_Inner7.nexus', 'tree_ORTHOMCL256_2_Inner8.nexus'], 'tree_ORTHOMCL256_Inner5.nexus': ['tree_ORTHOMCL256_2_Inner4.nexus'], 'tree_ORTHOMCL256_Inner6.nexus': ['tree_ORTHOMCL256_2_Inner4.nexus'], 'tree_ORTHOMCL256_Inner7.nexus': ['tree_ORTHOMCL256_2_Inner4.nexus'], 'tree_ORTHOMCL256_Inner8.nexus': ['tree_ORTHOMCL256_2_Inner4.nexus']}  
    #     2: {'tree_ORTHOMCL256_Inner1.nexus': ['tree_ORTHOMCL256_2_Inner1.nexus', 'tree_ORTHOMCL256_2_Inner2.nexus', 'tree_ORTHOMCL256_2_Inner3.nexus', 'tree_ORTHOMCL256_2_Inner5.nexus', 'tree_ORTHOMCL256_2_Inner6.nexus', 'tree_ORTHOMCL256_2_Inner7.nexus', 'tree_ORTHOMCL256_2_Inner8.nexus'], 'tree_ORTHOMCL256_Inner2.nexus': ['tree_ORTHOMCL256_2_Inner1.nexus', 'tree_ORTHOMCL256_2_Inner2.nexus', 'tree_ORTHOMCL256_2_Inner3.nexus', 'tree_ORTHOMCL256_2_Inner5.nexus', 'tree_ORTHOMCL256_2_Inner6.nexus', 'tree_ORTHOMCL256_2_Inner7.nexus', 'tree_ORTHOMCL256_2_Inner8.nexus'], 'tree_ORTHOMCL256_Inner3.nexus': ['tree_ORTHOMCL256_2_Inner1.nexus', 'tree_ORTHOMCL256_2_Inner2.nexus'], 'tree_ORTHOMCL256_Inner5.nexus': ['tree_ORTHOMCL256_2_Inner1.nexus', 'tree_ORTHOMCL256_2_Inner2.nexus'], 'tree_ORTHOMCL256_Inner6.nexus': ['tree_ORTHOMCL256_2_Inner1.nexus', 'tree_ORTHOMCL256_2_Inner2.nexus'], 'tree_ORTHOMCL256_Inner7.nexus': ['tree_ORTHOMCL256_2_Inner1.nexus', 'tree_ORTHOMCL256_2_Inner2.nexus'], 'tree_ORTHOMCL256_Inner8.nexus': ['tree_ORTHOMCL256_2_Inner1.nexus', 'tree_ORTHOMCL256_2_Inner2.nexus']}
    #     3: {'tree_ORTHOMCL256_Inner3.nexus': ['tree_ORTHOMCL256_2_Inner3.nexus', 'tree_ORTHOMCL256_2_Inner5.nexus', 'tree_ORTHOMCL256_2_Inner6.nexus', 'tree_ORTHOMCL256_2_Inner7.nexus', 'tree_ORTHOMCL256_2_Inner8.nexus'], 'tree_ORTHOMCL256_Inner5.nexus': ['tree_ORTHOMCL256_2_Inner3.nexus'], 'tree_ORTHOMCL256_Inner6.nexus': ['tree_ORTHOMCL256_2_Inner3.nexus'], 'tree_ORTHOMCL256_Inner7.nexus': ['tree_ORTHOMCL256_2_Inner3.nexus'], 'tree_ORTHOMCL256_Inner8.nexus': ['tree_ORTHOMCL256_2_Inner3.nexus']}
    #     4: {'tree_ORTHOMCL256_Inner5.nexus': ['tree_ORTHOMCL256_2_Inner5.nexus', 'tree_ORTHOMCL256_2_Inner6.nexus', 'tree_ORTHOMCL256_2_Inner7.nexus', 'tree_ORTHOMCL256_2_Inner8.nexus'], 'tree_ORTHOMCL256_Inner6.nexus': ['tree_ORTHOMCL256_2_Inner5.nexus'], 'tree_ORTHOMCL256_Inner7.nexus': ['tree_ORTHOMCL256_2_Inner5.nexus'], 'tree_ORTHOMCL256_Inner8.nexus': ['tree_ORTHOMCL256_2_Inner5.nexus']}
    #     5: {'tree_ORTHOMCL256_Inner6.nexus': ['tree_ORTHOMCL256_2_Inner6.nexus', 'tree_ORTHOMCL256_2_Inner7.nexus', 'tree_ORTHOMCL256_2_Inner8.nexus'], 'tree_ORTHOMCL256_Inner7.nexus': ['tree_ORTHOMCL256_2_Inner6.nexus'], 'tree_ORTHOMCL256_Inner8.nexus': ['tree_ORTHOMCL256_2_Inner6.nexus']}
    #     6: {'tree_ORTHOMCL256_Inner7.nexus': ['tree_ORTHOMCL256_2_Inner7.nexus', 'tree_ORTHOMCL256_2_Inner8.nexus'], 'tree_ORTHOMCL256_Inner8.nexus': ['tree_ORTHOMCL256_2_Inner7.nexus']}
    #     8: {'tree_ORTHOMCL256_Inner8.nexus': ['tree_ORTHOMCL256_2_Inner8.nexus']}
    # }
    # 2: {
    #     1: {'tree_ORTHOMCL256_2_Inner4.nexus': ['tree_ORTHOMCL256_Inner4.nexus', 'tree_ORTHOMCL256_Inner5.nexus', 'tree_ORTHOMCL256_Inner6.nexus', 'tree_ORTHOMCL256_Inner7.nexus', 'tree_ORTHOMCL256_Inner8.nexus'], 'tree_ORTHOMCL256_2_Inner5.nexus': ['tree_ORTHOMCL256_Inner4.nexus'], 'tree_ORTHOMCL256_2_Inner6.nexus': ['tree_ORTHOMCL256_Inner4.nexus'], 'tree_ORTHOMCL256_2_Inner7.nexus': ['tree_ORTHOMCL256_Inner4.nexus'], 'tree_ORTHOMCL256_2_Inner8.nexus': ['tree_ORTHOMCL256_Inner4.nexus']}
    #     2: {'tree_ORTHOMCL256_2_Inner1.nexus': ['tree_ORTHOMCL256_Inner1.nexus', 'tree_ORTHOMCL256_Inner2.nexus', 'tree_ORTHOMCL256_Inner3.nexus', 'tree_ORTHOMCL256_Inner5.nexus', 'tree_ORTHOMCL256_Inner6.nexus', 'tree_ORTHOMCL256_Inner7.nexus', 'tree_ORTHOMCL256_Inner8.nexus'], 'tree_ORTHOMCL256_2_Inner2.nexus': ['tree_ORTHOMCL256_Inner1.nexus', 'tree_ORTHOMCL256_Inner2.nexus', 'tree_ORTHOMCL256_Inner3.nexus', 'tree_ORTHOMCL256_Inner5.nexus', 'tree_ORTHOMCL256_Inner6.nexus', 'tree_ORTHOMCL256_Inner7.nexus', 'tree_ORTHOMCL256_Inner8.nexus'], 'tree_ORTHOMCL256_2_Inner3.nexus': ['tree_ORTHOMCL256_Inner1.nexus', 'tree_ORTHOMCL256_Inner2.nexus'], 'tree_ORTHOMCL256_2_Inner5.nexus': ['tree_ORTHOMCL256_Inner1.nexus', 'tree_ORTHOMCL256_Inner2.nexus'], 'tree_ORTHOMCL256_2_Inner6.nexus': ['tree_ORTHOMCL256_Inner1.nexus', 'tree_ORTHOMCL256_Inner2.nexus'], 'tree_ORTHOMCL256_2_Inner7.nexus': ['tree_ORTHOMCL256_Inner1.nexus', 'tree_ORTHOMCL256_Inner2.nexus'], 'tree_ORTHOMCL256_2_Inner8.nexus': ['tree_ORTHOMCL256_Inner1.nexus', 'tree_ORTHOMCL256_Inner2.nexus']}
    #     3: {'tree_ORTHOMCL256_2_Inner3.nexus': ['tree_ORTHOMCL256_Inner3.nexus', 'tree_ORTHOMCL256_Inner5.nexus', 'tree_ORTHOMCL256_Inner6.nexus', 'tree_ORTHOMCL256_Inner7.nexus', 'tree_ORTHOMCL256_Inner8.nexus'], 'tree_ORTHOMCL256_2_Inner5.nexus': ['tree_ORTHOMCL256_Inner3.nexus'], 'tree_ORTHOMCL256_2_Inner6.nexus': ['tree_ORTHOMCL256_Inner3.nexus'], 'tree_ORTHOMCL256_2_Inner7.nexus': ['tree_ORTHOMCL256_Inner3.nexus'], 'tree_ORTHOMCL256_2_Inner8.nexus': ['tree_ORTHOMCL256_Inner3.nexus']}
    #     4: {'tree_ORTHOMCL256_2_Inner5.nexus': ['tree_ORTHOMCL256_Inner5.nexus', 'tree_ORTHOMCL256_Inner6.nexus', 'tree_ORTHOMCL256_Inner7.nexus', 'tree_ORTHOMCL256_Inner8.nexus'], 'tree_ORTHOMCL256_2_Inner6.nexus': ['tree_ORTHOMCL256_Inner5.nexus'], 'tree_ORTHOMCL256_2_Inner7.nexus': ['tree_ORTHOMCL256_Inner5.nexus'], 'tree_ORTHOMCL256_2_Inner8.nexus': ['tree_ORTHOMCL256_Inner5.nexus']}
    #     5: {'tree_ORTHOMCL256_2_Inner6.nexus': ['tree_ORTHOMCL256_Inner6.nexus', 'tree_ORTHOMCL256_Inner7.nexus', 'tree_ORTHOMCL256_Inner8.nexus'], 'tree_ORTHOMCL256_2_Inner7.nexus': ['tree_ORTHOMCL256_Inner6.nexus'], 'tree_ORTHOMCL256_2_Inner8.nexus': ['tree_ORTHOMCL256_Inner6.nexus']}
    #     6: {'tree_ORTHOMCL256_2_Inner7.nexus': ['tree_ORTHOMCL256_Inner7.nexus', 'tree_ORTHOMCL256_Inner8.nexus'], 'tree_ORTHOMCL256_2_Inner8.nexus': ['tree_ORTHOMCL256_Inner7.nexus']}
    #     8: {'tree_ORTHOMCL256_2_Inner8.nexus': ['tree_ORTHOMCL256_Inner8.nexus']}
    # }
    # 3: {}
    # 4: {}
    
    # Criação do dicionário de similariadades de subárvore ##
    maf_start_time = timeit.default_timer()
    
    final_maf_database = {}
    final_max_maf = 0

    maf_databases = []
    subtrees = []
    
    # open input_file and read the data
    for input_file_name in input_files:
        file = os.path.join(INPUT_PATH, input_file_name)
        with open(file, 'r') as f:
            file_data = json.load(f)
            file_subtrees = file_data.get('subtrees')
            subtrees.append(file_subtrees)
            file_mafdb = file_data.get('maf_database')
            maf_databases.append(file_mafdb)

    for n1_mafdb in maf_databases:
        # print(f"___________ N1 - item: {n1_item} _______________")
        for n2_grade, n2_dict in n1_mafdb.items():
            # print(f"___________ N2 - grade: {n2_grade}  _______________")
            final_max_maf = max(final_max_maf, du.parse_int(n2_grade))
            # se o id do grau de similaridade não existe no dicionário de similaridades
            # então cria-se uma nova entrada
            if n2_grade not in final_maf_database:
                final_maf_database[n2_grade] = {}
            for n3_subtree, n3_subtrees in n2_dict.items():
                # print(f'>> N3: {n3_subtree}: {n3_subtrees} \n')
                # para um determinado grau de similaridade, adiciona-se a lista de subárvores similares em maf_database
                if n3_subtree not in final_maf_database[n2_grade]:
                    final_maf_database[n2_grade][n3_subtree] = n3_subtrees
                else:
                    raise ValueError(f"Subtree {n3_subtree} already exists in maf_database[{n2_grade}]!!")
            # print("_______________________________")

    # print(maf_database)

    produced_files = mdcc.write_maf_database(subtrees, final_maf_database, final_max_maf, OUTPUT_PATH)

    maf_end_time = timeit.default_timer()
    maf_time_ms = (maf_end_time - maf_start_time) * 1000
    
    logger.info(f'MAF_DATABASE_AGGREGATOR RequestId: {request_id}\t Duration: {maf_time_ms} ms\t InputLength: {len(maf_databases)}\t MaxMaf: {final_max_maf}\t MafDatabase: {final_maf_database}')

    # Upload output files ##
    dau.handle_produced_files(request_id, provider, produced_files, OUTPUT_PATH, s3_bucket, s3_key_output, logger)
 
    function_end_time = timeit.default_timer()
    function_duration_ms = (function_end_time - function_start_time) * 1000
    
    # "message": "END RequestId: 1c07a9af-e804-4d70-a287-54cde8ee7192\n",
    logger.info(f'END RequestId: {request_id}\t Activity: {activity}\t Provider: {provider}')

    # "message": "REPORT RequestId: 1c07a9af-e804-4d70-a287-54cde8ee7192\tDuration: 272.49 ms\tBilled Duration: 273 ms\tMemory Size: 2048 MB\tMax Memory Used: 111 MB\tInit Duration: 757.10 ms\t\n",
    logger.info(f'REPORT RequestId: {request_id}\t Duration: {function_duration_ms} ms\t Billed Duration: {math.ceil(function_duration_ms)} ms\t Memory Size: MB\t Max Memory Used: MB\t Init Duration: ms\t\n')

     
    return {
            "request_id" : request_id,
            "data" : produced_files
        }