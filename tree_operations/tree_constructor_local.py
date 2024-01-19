from tree_constructor_core import *
import boto3

# Substitua pelo caminho de entrada dos aquivos
PATH_BASE = 'tree_operations'
PATH_DATA = '_data'
PATH_LIB  = '_lib'
PATH_INPUT  = os.path.join(PATH_BASE, PATH_DATA, 'testset') # Localização dos arquivos de entrada
PATH_OUTPUT = os.path.join(PATH_BASE, PATH_DATA, 'out', 'trees') # Localização dos arquivos de árvores finais

# Usado para escrever arquivos 'nopipe' durante o processo de validação
PATH_TMP = os.path.join(PATH_BASE, PATH_DATA, 'tmp')  # '/tmp' is lambda local folder

# PATH_CLUSTALW = os.path.join(PATH_BASE, PATH_LIB, 'opt', 'python', 'clustalw-2.1-linux-x86_64-libcppstatic')
PATH_CLUSTALW = os.path.join(PATH_BASE, PATH_LIB, 'opt', 'python', 'ClustalW2')

# Formato das sequências
DATA_FORMAT = 'nexus' # newick ou nexus

s3 = boto3.client('s3')

def main():
    
    print("Estado do ambiente de execução")
    print('pwd:', os.getcwd())
    
    #
    # ## Limpeza arquivos antigos ##
    #
    remove_files(PATH_TMP)
    remove_files(PATH_OUTPUT)

    #
    # ## PERCORRER E MANIPULAR DIRETORIO ##
    # 
    # listagem de arquivos
    files = os.listdir(PATH_INPUT)
    
    for name_file in files:
        print("Reading file %s" % name_file)
        constructor_tree(name_file, PATH_INPUT, PATH_TMP, PATH_OUTPUT, PATH_CLUSTALW, DATA_FORMAT)

   
if __name__ == '__main__':
    main()
