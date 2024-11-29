import os, timeit, json
from denethor.utils.aws import aws_utils as dau
import maf_database_creator_core as mdcc
from denethor.utils import file_utils as dfu, log_handler as dlh, utils as du

def handler(event, context):

    request_id = du.resolve_request_id(context)
    execution_id = du.get_execution_id(event)
    execution_env = du.get_env_properties(event)
    logger = dlh.get_logger(execution_id, 'maf_database_aggregator', execution_env)

    du.log_env_info(execution_env, logger)

    path_params = execution_env.get('path_params')
    TMP_PATH = path_params.get('tmp') # usado para escrever arquivos 'nopipe' durante o processo de validação
    INPUT_PATH = path_params.get('mafdb')
    OUTPUT_PATH = path_params.get('mafdb')

    bucket_params = execution_env.get('bucket_params')
    s3_params = {
        'env_name': execution_env.get('env_name'),
        'bucket': bucket_params.get('bucket_name'),
        'input_key': bucket_params.get('key_mafdb_files'),
        'output_key': bucket_params.get('key_mafdb_files')
    }
    
    # Cleaning old temporary files and creating directories ##
    # dfu.remove_files(TMP_PATH)
    dfu.create_directory_if_not_exists(INPUT_PATH, OUTPUT_PATH, TMP_PATH)
    
    # Get the input_file from the payload
    input_fles = event.get('input_data')

    # Download input files ##
    dau.handle_consumed_files(request_id, input_fles, INPUT_PATH, s3_params)



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
    start_time = timeit.default_timer()
    
    final_maf_database = {}
    final_max_maf = 0

    maf_databases = []
    subtrees = []
    
    # open input_file and read the data
    for input_file_name in input_fles:
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

    final_mafdb_file = mdcc.write_maf_database(subtrees, final_maf_database, final_max_maf, OUTPUT_PATH)

    end_time = timeit.default_timer()
    maf_time_ms = (end_time - start_time) * 1000
    
    logger.info(f'MAF_DATABASE_AGGREGATOR RequestId: {request_id}\t Duration: {maf_time_ms} ms\t InputLength: {len(maf_databases)}\t MaxMaf: {final_max_maf}\t MafDatabase: {final_maf_database}')

    # Upload output files ##
    dau.handle_produced_files(request_id, final_mafdb_file, OUTPUT_PATH, s3_params)

    return {
            "request_id" : request_id,
            "data" : final_mafdb_file
        }
        

