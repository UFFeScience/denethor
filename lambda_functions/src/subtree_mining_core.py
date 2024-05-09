from file_utils import *
from dendropy import Tree
from Bio import Phylo
import os
import time

#
# ## Exibe subárvore ##
#
def print_trees_in_directory(directory, data_format):
    for filename in os.listdir(directory):
        if filename.endswith(".nexus"):
            file_path = os.path.join(directory, filename)

            print(filename.upper() + "\n")
            tree = Tree.get_from_path(file_path, data_format)
            tree.print_plot()


#
# ## Construtor de subárvores ##
#
def subtree_constructor(tree_name, input_tree_path, output_subtree_path, data_format):
    
    start_time = timeit.default_timer()

    match data_format:
        case 'nexus':
            DATA_FORMAT = 'nexus' # Nexus: 'nexus'
        case 'newick':
            DATA_FORMAT = 'nwk' # Newick: 'nwk'
    
    # Leitura do arquido da árvore
    print(f"\nReading tree file {tree_name}")
    tree_file = os.path.join(input_tree_path, tree_name)            
    tree = Phylo.read(tree_file, data_format)

    #Lista caminhos das subárvores (que posteriormente serão utilizadas para compor a matriz de subárvores)
    list_subtree = []

    # Salva o arquivo da subárvore
    tree_name_prefix = tree_name.rsplit(".", 1)[0]

    for clade in tree.find_clades():
        subtree = Phylo.BaseTree.Tree(clade)
        if subtree.count_terminals() > 1:
            subtree_name = f'{tree_name_prefix}_{clade.name}.{DATA_FORMAT}'
            subtree_file = os.path.join(output_subtree_path, subtree_name)
            Phylo.write(subtree, subtree_file, data_format)
            list_subtree.append(subtree_name)
            print(f"Subtree file {subtree_name} was created!")

    end_time = timeit.default_timer()
    subtree_duration_ms = (end_time - start_time) * 1000
    print(f'Tempo de construção dos arquivos de subárvores de {tree_name}: {subtree_duration_ms} milissegundos')

    return list_subtree, subtree_duration_ms


# 
# ## Preencher as células vazias com o valor de preenchimento ##
#
def fill_matrix(matrix, value):
    max_rows = len(matrix)
    max_columns = max(len(row) for row in matrix)
    for row in matrix:
        while len(row) < max_columns:
            row.append(value)
    print(f'max_rows= {max_rows} | max_columns= {max_columns}')
    
    return matrix


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


def maf_database_create(subtree_matrix, path, data_format):
    
    print(f'maf_database_create start time: {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}')

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
    
    return dict_maf_database, max_maf
