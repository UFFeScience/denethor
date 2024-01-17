from tree_operations.tree_constructor_core import *
import boto3

# Substitua pelo caminho de entrada dos aquivos
PATH_INPUT  = '_data/testset' # Armazena arquivos de entrada
PATH_OUTPUT = '_data/out/trees' # Armazena os arquivos de árvores finais

# Usado para escrever arquivos 'nopipe' durante o processo de validação
PATH_TMP = '_data/tmp'  # '/tmp' is lambda local folder

PATH_CLUSTALW = '_lib/opt/python/clustalw-2.1-linux-x86_64-libcppstatic'

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
    dir = os.path.join(PATH_INPUT)
    files = os.listdir(dir)
    
    for name_file in files:
        print("Reading file %s" % name_file)
        constructor_tree(name_file, PATH_INPUT, PATH_TMP, PATH_OUTPUT, PATH_CLUSTALW, DATA_FORMAT)

   
if __name__ == '__main__':
    main()
