from tree_sub_find_core import *
import boto3

# Substitua pelo caminho de entrada dos aquivos
PATH_BASE = 'tree_operations'
PATH_DATA = '_data'
PATH_LIB  = '_lib'
PATH_INPUT  = os.path.join(PATH_BASE, PATH_DATA, 'out', 'trees') # Localização dos arquivos de entrada
PATH_OUTPUT = os.path.join(PATH_BASE, PATH_DATA, 'out', 'subtrees') # Localização dos arquivos de árvores finais

DATA_FORMAT = 'nexus' # newick ou nexus

def main():

    print("******* Estado do ambiente de execução *******")
    print('pwd:', os.getcwd())

    #
    # ## Limpeza arquivos antigos ##
    #
    remove_files(PATH_OUTPUT)

    #
    # ## PERCORRER E MANIPULAR DIRETORIO ##
    # 
    # Diretório de entrada de árvores
    files = os.listdir(PATH_INPUT)

    # matriz com todas as subárvores
    matriz_subtree = []

    for name_file in files:
        print("Reading file %s" % name_file)     
        file_path = os.path.join(PATH_INPUT, name_file)
        matriz_subtree.append(sub_tree(file_path, name_file, PATH_OUTPUT, DATA_FORMAT))
    
    # máximo de colunas
    max_columns = max(len(row) for row in matriz_subtree)
    
    # máximo de linhas
    max_rows = len(matriz_subtree)

    print('max_rows=', max_rows, ' | ', 'max_columns=', max_columns)
    preencher_matriz(matriz_subtree, max_columns, None)

    # for linha in matriz_subtree:
    #     print(linha)
    
    dict_maf_database = {}

    # dict_maf_database = fill_dict(dict_maf_database, max_columns)
    fill_dict(dict_maf_database, max_columns)
    print('dict_maf_database:', dict_maf_database)
    
    max_maf = 0
    for i in range(max_rows):
        for j in range(max_columns):
            dict_aux = {}
            for k in range(max_rows):
                for l in range(max_columns):
                    if i != k:
                        g_maf = grade_maf(matriz_subtree[i][j], matriz_subtree[k][l], PATH_OUTPUT, DATA_FORMAT)
                        # print('g_maf=',g_maf)

                        if max_maf <= g_maf:
                            max_maf = g_maf

                        if g_maf is not False and g_maf >= 1:
                            if g_maf not in dict_maf_database:
                                dict_maf_database[g_maf] = {}
                            if matriz_subtree[i][j] not in dict_maf_database[g_maf]:
                                dict_maf_database[g_maf][matriz_subtree[i][j]] = []
                            dict_maf_database[g_maf][matriz_subtree[i][j]].append(matriz_subtree[k][l])

    print('max_maf:',max_maf)

    print('dict_maf_database:', dict_maf_database)
    # for i, j in dict_maf_database.items():
    #     print(i,j)
    #     for key, val in j.items():
    #         # print(i, key, val)
    #         continue

    
if __name__ == '__main__':
    main()