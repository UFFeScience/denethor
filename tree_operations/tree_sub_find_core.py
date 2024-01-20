#
# O formato das Sequências de proteínas deve ser especificado em `DATA_FORMATT`
#
from Bio import Phylo
from dendropy import Tree
import os
from tree_utils import *


#
# Exibe subárvore
#
def print_trees_in_directory(directory, data_format):
    for filename in os.listdir(directory):
        if filename.endswith(".nexus"):
            file_path = os.path.join(directory, filename)

            print(filename.upper() + "\n")
            tree = Tree.get_from_path(file_path, data_format)
            tree.print_plot()


#
# Construtor de subárvores
#
def sub_tree_constructor(path_file, name_subtree, path_output, data_format):
    
    match data_format:
        case 'nexus':
            EXTENTION_FORMAT = 'nexus' # Nexus: 'nexus'
        case 'newick':
            EXTENTION_FORMAT = 'nwk' # Newick: 'nwk'
    
    # Salva a árvore
    tree = Phylo.read(path_file, data_format)
    name_subtree = name_subtree.rsplit(".", 1)[0]

    #Lista caminhos das subárvores (que posteriormente serão utilizadas para compor a matriz de subárvores)
    row_subtree = []

    for clade in tree.find_clades():
        subtree = Phylo.BaseTree.Tree(clade)
        if subtree.count_terminals() > 1:
            name_file_out = f'{name_subtree}_{clade.name}.{EXTENTION_FORMAT}'
            file_path_out = os.path.join(path_output, name_file_out)
            Phylo.write(subtree, file_path_out, data_format)
            row_subtree.append(name_file_out)

    return row_subtree


#
# Preencher as células vazias com o valor de preenchimento
#
def fill_matrix(matrix, value):
    max_rows = len(matrix)
    max_columns = max(len(row) for row in matrix)
    for row in matrix:
        while len(row) < max_columns:
            row.append(value)
    print('max_rows=', max_rows, ' | ', 'max_columns=', max_columns)
    
    return matrix


#
# Comparação das subárvores
#
def grade_maf(path_1, path_2, path_output, data_format):
    if(path_1 is None or path_2 is None):
        return -1
    grau = 0

    subtree_1 = Phylo.read(os.path.join(path_output, path_1), data_format)
    subtree_2 = Phylo.read(os.path.join(path_output, path_2), data_format)

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


def create_maf_database(subtree_matrix, path_output, data_format):

    max_rows = len(subtree_matrix)
    max_columns = max(len(row) for row in subtree_matrix)

    dict_maf_database = {i: {} for i in range(1, max_columns)}
    print('Empty dict_maf_database:', dict_maf_database)
    
    max_maf = 0
    for i in range(max_rows):
        for j in range(max_columns):
            dict_aux = {}
            for k in range(max_rows):
                for l in range(max_columns):
                    if i != k:
                        g_maf = grade_maf(subtree_matrix[i][j], subtree_matrix[k][l], path_output, data_format)
                        # print('g_maf=',g_maf)

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


