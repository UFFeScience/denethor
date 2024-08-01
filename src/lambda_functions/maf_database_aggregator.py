import timeit
from denethor_utils import log_handler as dlh, utils as du

def handler(event, context):

    request_id = du.get_request_id(context)
    execution_id = du.get_execution_id(event)
    execution_env = du.get_execution_env(event)
    logger = dlh.get_logger(execution_id, execution_env)

    du.log_env_info(execution_env, logger)

    #
    ## Get the input_file from the payload
    #
    input_data = event.get('input_data')
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
    
    #
    ## Criação do dicionário de similariadades de subárvore ##
    #
    
    start_time = timeit.default_timer()

    
    maf_database = {}
    max_maf = 0
    
    n1_list = input_data
    for n1_item in n1_list:
        print(f"___________ N1 - item: {n1_item} _______________")
        for n2_grade, n2_dict in n1_item.items():
            print(f"___________ N2 - grade: {n2_grade}  _______________")
            max_maf = max(max_maf, du.parse_int(n2_grade))
            # se o id do grau de similaridade não existe no dicionário de similaridades
            # então cria-se uma nova entrada
            if n2_grade not in maf_database:
                maf_database[n2_grade] = {}
            for n3_subtree, n3_subtree_list in n2_dict.items():
                print(f'>> N3: {n3_subtree}: {n3_subtree_list} \n')
                # para um determinado grau de similaridade, adiciona-se a lista de subárvores similares em maf_database
                if n3_subtree not in maf_database[n2_grade]:
                    maf_database[n2_grade][n3_subtree] = n3_subtree_list
                else:
                    raise ValueError(f"Subtree {n3_subtree} already exists in maf_database[{n2_grade}]!!")
            print("_______________________________")

    # print(maf_database)

    end_time = timeit.default_timer()
    maf_time_ms = (end_time - start_time) * 1000
    
    logger.info(f'MAF_DATABASE_AGGREGATE RequestId: {request_id}\t InputDataCount: {len(input_data)}\t Duration: {maf_time_ms} ms\t MaxMaf: {max_maf}\t MafDatabase: {maf_database}')

    #
    ## Upload output files ##
    #
    # du.handle_produced_files(request_id, produced_files, OUTPUT_PATH, event)
    
    return {
            "request_id" : request_id,
            "produced_data" : maf_database
        }
        

