import os, copy
from dendropy import Tree
from Bio import Phylo
from lambda_functions.src.file_utils import *

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
def subtree_constructor(input_tree_files, input_tree_path, output_subtree_path, file_format):
    
    start_time = timeit.default_timer()
    
    if not isinstance(input_tree_files, list):
        files = [input_tree_files]
    else:
        files = input_tree_files

    match file_format:
        case 'nexus':
            DATA_FORMAT = 'nexus' # Nexus: 'nexus'
        case 'newick':
            DATA_FORMAT = 'nwk' # Newick: 'nwk'
    
    produced_files = []
    
    for tree_name in files:

        # Leitura do arquido da árvore
        print(f"\nReading tree file {tree_name}")
        tree_file = os.path.join(input_tree_path, tree_name)            
        tree = Phylo.read(tree_file, file_format)

        #Lista caminhos das subárvores (que posteriormente serão utilizadas para compor a matriz de subárvores)
        subtree_files = []

        # Salva o arquivo da subárvore
        tree_name_prefix = tree_name.rsplit(".", 1)[0]

        for clade in tree.find_clades():
            subtree = Phylo.BaseTree.Tree(clade)
            if subtree.count_terminals() > 1:
                subtree_name = f'{tree_name_prefix}_{clade.name}.{DATA_FORMAT}'
                subtree_file = os.path.join(output_subtree_path, subtree_name)
                Phylo.write(subtree, subtree_file, file_format)
                subtree_files.append(subtree_name)
                print(f"Subtree file {subtree_name} was created!")

        subtree_files.sort()
        produced_files.extend(subtree_files)

    end_time = timeit.default_timer()
    duration_ms = (end_time - start_time) * 1000
    print(f'Tempo de construção dos arquivos de subárvores de {input_tree_files}: {duration_ms} milissegundos')

    return produced_files, duration_ms


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