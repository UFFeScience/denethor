from tree_operations.tree_sub_find_core import *
import boto3

# Substitua pelo caminho de entrada dos aquivos
# O bucket e path de entrada dos arquivos de subárvore
BUCKET_INPUT = 'mribeiro-bucket-output-tree'
PATH_INPUT  = ''

BUCKET_OUTPUT = 'mribeiro-bucket-output-subtree'
PATH_OUTPUT = '' # Armazena os arquivos de subárvores finais na raiz do bucket

# Armazena arquivos de entrada que chegam no S3
PATH_TMP_INPUT = '/tmp/input'

# Armazena os arquivos de árvores finais que serão copiados para o S3
PATH_TMP_OUTPUT = '/tmp/subtrees'

DATA_FORMAT = 'nexus' # newick ou nexus

s3 = boto3.client('s3')

def lambda_handler(event, context):

    print("******* Estado do ambiente de execução *******")
    print('pwd:', os.getcwd())
    print('/:', os.listdir("/"))
    print('/opt: ', os.listdir("/opt"))
    print('/opt/python: ', os.listdir("/opt/python"))
    print('/var/task: ', os.listdir("/var/task"))

    #
    # ## Limpeza arquivos temporários ##
    #
    remove_files(PATH_TMP_OUTPUT)
    remove_files(PATH_TMP_INPUT) #comentar na execução local


    #
    # ## PERCORRER E MANIPULAR DIRETORIO ##
    # 
    # get your bucket and key from event data
    data_rec = event['Records'][0]['s3']
    s3_bucket = data_rec['bucket']['name']
    print("s3_bucket_input:", s3_bucket)

    
    #
    # List the tree files from bucket
    #
    response = s3.list_objects_v2(Bucket=s3_bucket, Prefix='', StartAfter='')
    s3_files = response["Contents"]
    for s3_file in s3_files:
        # key representa o path + nome do arquivo do s3
        s3_key = s3_file["Key"]
        print('file from s3:', s3_key)

        # basename representa o nome do arquivo
        name_file = os.path.basename(s3_key)
        name_file_path = os.path.join(PATH_TMP_INPUT, name_file)
        s3.download_file(s3_bucket, s3_key, name_file_path)
    
    
    
    # Diretório de entrada de árvores
    files = os.listdir(PATH_TMP_INPUT)

    # matriz com todas as subárvores
    matriz_subtree = []

    for name_file in files:

        print("Reading file %s" % name_file)     

        file_path = os.path.join(PATH_TMP_INPUT,name_file)
        matriz_subtree.append(sub_tree(file_path, name_file, PATH_TMP_OUTPUT, DATA_FORMAT))
    
    # máximo de colunas
    max_columns = max(len(row) for row in matriz_subtree)
    
    # máximo de linhas
    max_rows = len(matriz_subtree)

    print('max_rows=', max_rows, ' | ', 'max_columns=', max_columns)
    # matriz_subtree = preencher_matriz(matriz_subtree,None)
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

                        g_maf = grade_maf(matriz_subtree[i][j], matriz_subtree[k][l], PATH_TMP_OUTPUT, DATA_FORMAT)
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

    
    #
    # ## Copiar arquivos tree para o S3 ##
    #
    dir_trees = os.path.join(PATH_TMP_OUTPUT)
    
    for tree_file_name in os.listdir(dir_trees):
        tree_file_path = os.path.join(dir_trees, tree_file_name)
        s3_output_key = os.path.join(PATH_OUTPUT, tree_file_name)
        
        # print('tree_file_name:' , tree_file_name)
        print('tree_file_path:' , tree_file_path)

        
        url = upload_file_to_S3(tree_file_path, BUCKET_OUTPUT, s3_output_key, s3)
        
        print("url:", url)

    return "OK"
