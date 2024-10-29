from Bio import Phylo
import os, json, re, copy, time, timeit
import hashlib


# 
# ## Preencher as células vazias com o valor de preenchimento ##
#
def fill_matrix(matrix, value):
    
    max_rows = len(matrix)
    max_columns = max(len(row) for row in matrix)

    full_matrix = copy.deepcopy(matrix)
    
    for row in full_matrix:
        while len(row) < max_columns:
            row.append(value)
    print(f'max_rows= {max_rows} | max_columns= {max_columns}')
    
    return full_matrix


#
# ## Comparação das subárvores ##
#
def grade_maf(file_1, file_2, path, data_format):
    if(file_1 is None or file_2 is None):
        return -1
    grau = 0

    subtree_1 = Phylo.read(os.path.join(path, file_1), data_format)
    subtree_2 = Phylo.read(os.path.join(path, file_2), data_format)

    # Lista todas as clades ( folhas )
    list_1 = [i.name for i in subtree_1.get_terminals()]
    list_2 = [i.name for i in subtree_2.get_terminals()]

    sorted_list1 = sorted(list_1)
    sorted_list2 = sorted(list_2)

    for i in range(len(list_1)):
        for j in range(len(list_2)):
            if sorted_list1[i] == sorted_list2[j]:
                grau += 1
    return grau



def init_maf_database(matrix):
    # inicializando maf_database com espaços vazios
    max_columns = max(len(row) for row in matrix)
    maf = {i: {} for i in range(1, max_columns)}
    print(f'Empty dict_maf_database: {maf}')
    return maf


def maf_database_creator(subtrees: list, compare_matrix: list, input_path: str, output_path: str, data_format: str) -> str:    
    start_time = timeit.default_timer()

    maf_database: dict = None
    max_maf: int = 0

    sorted_subtrees = sorted(subtrees)
    sorted_compare_matrix= [sorted(row) for row in compare_matrix]
    

    if maf_database is None:
        maf_database = {}

    #subtrees equivale a uma linha da matriz de subárvores
    for main_file  in sorted_subtrees:
        print(f'subtree_matrix: processing file {main_file } of {sorted_subtrees}')
        
        for row in sorted_compare_matrix:
            # evitando comparações entre os arquivos de subárvores idênticos ou originados da mesma árvore
            if main_file in row:
                continue
            
            for current_file in row:
                # print(f'Comparing file {main_file} with {current_file}')
                g_maf = grade_maf(main_file , current_file, input_path, data_format)
                # print('g_maf=', g_maf)

                if max_maf < g_maf:
                    max_maf = g_maf

                if g_maf > 0:
                    if g_maf not in maf_database:
                        maf_database[g_maf] = {}
                    if main_file  not in maf_database[g_maf]:
                        maf_database[g_maf][main_file] = []
                    maf_database[g_maf][main_file].append(current_file)
    
    # for i, j in dict_maf_database.items():
    #     print(i,j)
    #     for key, val in j.items():
    #         # print(i, key, val)
    #         continue
    
    end_time = timeit.default_timer()
    maf_duration_ms = (end_time - start_time) * 1000
    print(f'Tempo de construção do maf_database: {maf_duration_ms} milissegundos')

    mafdb_file = write_maf_database(sorted_subtrees, maf_database, max_maf, output_path)
    
    return mafdb_file, maf_duration_ms




def write_maf_database(subtrees: list, maf_database: dict, max_maf: int, output_path: str) -> str:

    sorted_subtrees = sorted(subtrees)
    sorted_maf_database = {k: maf_database[k] for k in sorted(maf_database)}

    file_data = {
        "subtrees": sorted_subtrees,
        "max_maf": max_maf,
        "maf_database": sorted_maf_database
    }
    
    mafdb_identifier = generate_identifier(file_data)
    mafdb_name = f"mafdb_{mafdb_identifier}.json"
    mafdb_file = os.path.join(output_path, mafdb_name)

    with open(mafdb_file, 'w') as f:
        json.dump(file_data, f, indent=4)
    
    return mafdb_name


def generate_identifier(data_dict: dict) -> str:
    # Converte o dicionário em uma string JSON ordenada
    ordered_string = json.dumps(data_dict, sort_keys=True)
    
    # Calcula o hash da string ordenada
    return hashlib.sha256(ordered_string.encode()).hexdigest()
    



def maf_database_create_orig(subtree_matrix, path, data_format):
    
    start_time = timeit.default_timer()

    subtree_matrix = fill_matrix(subtree_matrix, value=None)

    max_rows = len(subtree_matrix)
    max_columns = max(len(row) for row in subtree_matrix)

    # inicializando dict_maf_database com espaços vazios
    dict_maf_database = {i: {} for i in range(1, max_columns)}
    print(f'Empty dict_maf_database: {dict_maf_database}')
    
    print(f'subtree_matrix: max_rows= {max_rows} | max_columns= {max_columns}')
    max_maf = 0
    for i in range(max_rows):
        print(f'subtree_matrix: processing    row {i} of {max_rows}')
        for j in range(max_columns):
            print(f'subtree_matrix: processing column {j} of {max_columns}')
            for k in range(max_rows):
                for l in range(max_columns):
                    if i != k:
                        print(f'Comparing [{i}][{j}]={subtree_matrix[i][j]} with [{k}][{l}]={subtree_matrix[k][l]}')
                        g_maf = grade_maf(subtree_matrix[i][j], subtree_matrix[k][l], path, data_format)
                        # print('g_maf=', g_maf)

                        if max_maf <= g_maf:
                            max_maf = g_maf

                        if g_maf >= 1:
                            if g_maf not in dict_maf_database:
                                dict_maf_database[g_maf] = {}
                            if subtree_matrix[i][j] not in dict_maf_database[g_maf]:
                                dict_maf_database[g_maf][subtree_matrix[i][j]] = []
                            dict_maf_database[g_maf][subtree_matrix[i][j]].append(subtree_matrix[k][l])
    
    # for i, j in dict_maf_database.items():
    #     print(i,j)
    #     for key, val in j.items():
    #         # print(i, key, val)
    #         continue
    
    end_time = timeit.default_timer()
    maf_duration_ms = (end_time - start_time) * 1000
    print(f'Tempo de construção do maf_database: {maf_duration_ms} milissegundos')

    return dict_maf_database, max_maf, maf_duration_ms






