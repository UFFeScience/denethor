#
# ALINHAMENTO E GERAÇÃO DE ÁRVORE FILOGENÉTICA
# IMPORTANTE LEMBRAR:
# 
# - É necessário ter o clustalw instalado
# - Sequências de proteínas devem ser fornecidas do diretório especificado em `input_path`
# - O formato das Sequências de proteínas deve ser especificado em `OUTPUT_FORMAT`
# 
# IMPORTS E CONFIGURAÇÃO DO DIRETÓRIO BASE
#
from Bio.Align.Applications import ClustalwCommandline
from Bio import AlignIO, Phylo, SeqIO
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor
from file_operations import *
import os

       
#
# ## VALIDADORES ##
# 
#Função que verifica se todas as sequências são proteínas válidas no formato FASTA
def validate_sequences(file_path):
    # Define os caracteres válidos para uma sequência de proteína.
    valid_characters = set('ACDEFGHIKLMNPQRSTVWY')
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('>'):
                    continue  # Pula a linha de cabeçalho
                sequence = line.strip()
                if not set(sequence).issubset(valid_characters):
                    return False
    except FileNotFoundError:
        print(f'O arquivo {file_path} não foi encontrado.')
        return False

    return True

def duplicate_names(file_path):
    name_count = {}
    try:
        for record in SeqIO.parse(file_path, 'fasta'):
            name = record.id
            name_count[name] = name_count.get(name, 0) + 1
            if name_count[name] > 1:
                return True
    except FileNotFoundError:
        print(f'O arquivo {file_path} não foi encontrado.')
        return False

    return False


#
# ## TRATAMENTO DE SEQUENCIA ##
# 
def remove_pipe(name, path_in_fasta, path_tmp):
    sequences = list(SeqIO.parse(path_in_fasta, 'fasta'))
    # Criar um dicionário para armazenar as sequências únicas
    unique_sequences = {}
    # Iterar pelas sequências do arquivo de entrada
    for sequence in sequences:
        # Verificar se a sequência já existe no dicionário de sequências únicas
        if str(sequence.seq) not in unique_sequences:
            # Se a sequência é única, armazená-la no dicionário
            unique_sequences[str(sequence.seq)] = sequence
    # Criar uma lista de sequências únicas
    unique_sequences_list = list(unique_sequences.values())
    # Salvar as sequências únicas em um arquivo de saída
    output_file_tmp_nopipe = os.path.join(path_tmp, f'{name}_NoPipe')
    SeqIO.write(unique_sequences_list, output_file_tmp_nopipe, 'fasta')
    return output_file_tmp_nopipe



#
# ## CONSTRUTUOR ##
# 
# Mais informações sobre aplicações biopython e clustalwcommandline - https://biopython.org/docs/1.76/api/Bio.Align.Applications.html
def tree_constructor(file_name, input_path, tmp_path, output_path, clustalw_path, data_format):
    
    start_time = timeit.default_timer()

    file_name = os.path.basename(file_name)


    match data_format:
        case 'nexus':
            EXTENTION_FORMAT = 'nexus' # Nexus: 'nexus'
        case 'newick':
            EXTENTION_FORMAT = 'nwk' # Newick: 'nwk'
    
    #configurando caminhos relativos padrões do diretorio
    fasta_file = os.path.join(input_path, file_name)
    aln_file  = os.path.join(tmp_path, f'{file_name}.aln')
    dnd_file  = os.path.join(tmp_path, f'{file_name}.dnd')
    tree_file = os.path.join(output_path, f'tree_{file_name}.{EXTENTION_FORMAT}')

    # Em caso de nomes duplicados ou sequências inválidas
    if duplicate_names(fasta_file) or not(validate_sequences(fasta_file)):
        fasta_file = remove_pipe(file_name, fasta_file, tmp_path)

    # Executa o programa Clustalw para alinhar as sequências sem precisar da linha de comando.
    if not os.path.exists(clustalw_path):
        print(f'Sorry, directory {clustalw_path} do not exist.')
        
    clustalw_bin = os.path.join(clustalw_path,'clustalw2')
    clustalw_cline = ClustalwCommandline(clustalw_bin, infile=fasta_file, outfile=aln_file)
    
    #  Executa o comando ClustalW com base nos parâmetros definidos no objeto ClustalwCommandline e retorna os resultados da execução na forma de uma tupla de strings.
    clustalw_cline()

    # Mover o arquivo de saída .dnd (gerado no mesmo local do do arquivo de entrada) para o diretório 'resultados'
    path_curr_dnd = f'{fasta_file}.dnd'
    os.rename(path_curr_dnd, dnd_file)

    '''
    Clustalw_cline() - gera 2 arquivos de saida por padrão

    Nesse caso:
    - ORTHOMCL256.aln: Contendo a sequência de ORTHOMCL256 alinhada em formato clustal
    - ORTHOMCL256.dnd: Contendo informações sobre o agrupamento hierárquico das sequências alinhadas.
    '''

    # Abre o arquivo de alinhamento
    with open(aln_file, 'r') as handle:
        # O objeto MultipleSeqAlignment retornado é armazenado na variável.
        alignment = AlignIO.read(handle, 'clustal')

    # Calcula a matriz de distância
    # argumento 'identity', que indica que a distância entre as sequências será medida pelo número de identidades, ou seja, a fração de posições nas sequências que possuem o mesmo nucleotídeo ou aminoácido.
    calculator = DistanceCalculator('identity')
    # Calcula a matriz de distâncias entre as sequências
    distance_matrix = calculator.get_distance(alignment)

    # Constrói a árvore filogenética
    # Constrói árvores filogenéticas a partir de matrizes de distâncias entre sequências.
    constructor = DistanceTreeConstructor()
    tree = constructor.nj(distance_matrix)

    # Salva a árvore
    Phylo.write(tree, tree_file, EXTENTION_FORMAT)
    print(f'Writing file {tree_file}')

    end_time = timeit.default_timer()
    tree_duration_ms = (end_time - start_time) * 1000

    return tree_duration_ms
