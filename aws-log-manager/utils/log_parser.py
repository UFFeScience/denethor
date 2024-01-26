import re
from db.db_model import *
from db.repository import *
from db.conn import *
from utils.log_utils import *

def process_logs(request_id, logs):
    
    service_execution = ServiceExecution(request_id=request_id)
    
    for log in logs:
        
        service_execution.log_stream_name = log['logStreamName']
        
        log_parsed_dict = parse_log(log['message'])
        
        #   
        # Validations of request_id
        #
        if log_parsed_dict['RequestId'] is None:
            raise ValueError(f"Invalid request_id:{log_parsed_dict['RequestId']}")
        
        if service_execution.request_id != log_parsed_dict['RequestId']:
            raise ValueError(f"Error! Current request_id:{log_parsed_dict['RequestId']} | Expected request_id:{service_execution.request_id}")
        
        ##########

        match log_parsed_dict['LogType']:
            case 'START':
                process_start(service_execution, log['timestamp'])
            
            case 'END':
                process_end(service_execution, log['timestamp'])
            
            case 'REPORT':
                process_report(service_execution, log_parsed_dict)
            
            case 'FILE_DOWNLOAD':
                process_file(service_execution, log_parsed_dict, 'consumed')
            
            case 'FILE_UPLOAD':
                process_file(service_execution, log_parsed_dict, 'produced')
            
            case 'CONSUMED_FILES_INFO':
                process_total_file_info(service_execution, log_parsed_dict, 'consumed')
            
            case 'PRODUCED_FILES_INFO':
                process_total_file_info(service_execution, log_parsed_dict, 'produced')
            
            case 'SUBTREE_FILES_CREATE':
                process_subtree_info(service_execution, log_parsed_dict)
            
            case 'MAF_DATABASE_CREATE':
                process_maf_databse_info(service_execution, log_parsed_dict)
            
            case _:
                raise ValueError(f"Invalid log_type:{log_parsed_dict['LogType']}")

    return service_execution



# "timestamp": 1705599854279, "message": "START RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c Version: $LATEST\n"
def process_start(service_execution, timestamp):
    service_execution.start_time = to_datetime(timestamp)


# "timestamp": 1705599874327, "message": "END RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\n"
def process_end(service_execution, timestamp):
    service_execution.end_time = to_datetime(timestamp)


# "message": "REPORT RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\tDuration: 1010.14 ms\tBilled Duration: 1011 ms\tMemory Size: 128 MB\tMax Memory Used: 115 MB\tInit Duration: 918.52 ms\t\n"
def process_report(service_execution, log_dict: dict):
    service_execution.duration = parse_float(log_dict['Duration'])
    service_execution.billed_duration = parse_float(log_dict['Billed Duration'])
    service_execution.memory_size = parse_int(log_dict['Memory Size'])
    service_execution.max_memory_used = parse_int(log_dict['Max Memory Used'])
    service_execution.init_duration = parse_float(log_dict['Init Duration'])


# "message": "FILE_DOWNLOAD RequestId: c3df54b6-1da5-48b2-bec4-093b55c96692\t FileName: ORTHOMCL1\t Bucket: mribeiro-bucket-input\t FilePath: data/testset/ORTHOMCL1\t Duration: 407.83485699999744 ms\t FileSize: 1640 bytes\n"
# "message": "FILE_UPLOAD RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\t FileName: tree_ORTHOMCL1.nexus\t Bucket: mribeiro-bucket-output-tree\t FilePath: tree_ORTHOMCL1.nexus\t Duration: 292.6312569999965 ms\t FileSize: 339 bytes\n"
def process_file(service_execution, log_dict: dict, action_type: str):
    file = File(name=log_dict['FileName'], size=parse_int(log_dict['FileSize']), path=log_dict['FilePath'], bucket=log_dict['Bucket'])
    execution_file = ExecutionFile(transfer_duration=parse_float(log_dict['Duration']), action_type=action_type, file=file)
    service_execution.execution_files.append(execution_file)
    

# "message": "CONSUMED_FILES_INFO RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t NumFiles: 100 files\t TotalFilesSize: 36777 bytes\t Duration: 6933.13087699994 ms\n"
# "message": "PRODUCED_FILES_INFO RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t NumFiles: 335 files\t TotalFilesSize: 83697 bytes\t Duration: 17168.395734999875 ms\n"
def process_total_file_info(service_execution, log_dict: dict, action_type: str):
    if action_type == 'consumed':
        service_execution.num_consumed_files = parse_int(log_dict['NumFiles'])
        service_execution.total_consumed_files_size = parse_int(log_dict['TotalFilesSize'])
        service_execution.total_consumed_transfer_duration = parse_float(log_dict['Duration'])
    
    elif action_type == 'produced':
        service_execution.num_produced_files = parse_int(log_dict['NumFiles'])
        service_execution.total_produced_files_size = parse_int(log_dict['TotalFilesSize'])
        service_execution.total_produced_transfer_duration = parse_float(log_dict['Duration'])

# "message": "SUBTREE_FILES_CREATE RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t Duration: 795.8109850000028 ms\n"
def process_subtree_info(service_execution, log_dict: dict):
    subtree_stat = Statistics(name='subtree_duration', description='Tempo de execução da atividade de criação de subárvores')
    subtree_execution_stat = ExecutionStatistics(statistics=subtree_stat, value_float=parse_float(log_dict['Duration']))
    service_execution.execution_statistics.append(subtree_execution_stat)

# "message": "MAF_DATABASE_CREATE RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t MaxMaf: 5\t Duration: 485681.23013399995 ms\t MafDatabase: {1: {}, 2: {'tree_ORTHOMCL1_Inner3.nexus': ['tree_ORTHOMCL1977_Inner2.nexus', 'tree_ORTHOMCL1977_Inner1.nexus'],      (.......)     , 3: {}, 5: {'tree_ORTHOMCL1_Inner3.nexus': ['tree_ORTHOMCL1977_Inner3.nexus'],) 'tree_ORTHOMCL1977_Inner3.nexus': ['tree_ORTHOMCL1_Inner3.nexus']}}\n"
def process_maf_databse_info(service_execution, log_dict: dict):
    max_maf_stat = Statistics(name='max_maf', description='Maior valor de MAF encontrado no processamento dos arquivos de entrada')
    max_maf_execution_stat = ExecutionStatistics(statistics=max_maf_stat, value_integer=parse_int(log_dict['MaxMaf']))
    service_execution.execution_statistics.append(max_maf_execution_stat)
    
    maf_db_duration_stat = Statistics(name='maf_db_duration', description='Tempo de execução da atividade de criação do banco de dados MAF')
    maf_db_duration_execution_stat = ExecutionStatistics(statistics=maf_db_duration_stat, value_float=parse_float(log_dict['Duration']))
    service_execution.execution_statistics.append(maf_db_duration_execution_stat)
    
    maf_database_stat = Statistics(name='maf_database', description='Valor do dicionário "maf_database" obtido ao término do processo')
    maf_database_execution_stat = ExecutionStatistics(statistics=maf_database_stat, value_string=log_dict['MafDatabase'])
    service_execution.execution_statistics.append(maf_database_execution_stat)



def parse_log(log_string):
    # Separar o tipo de log do restante da string
    log_type, log_details = log_string.split(' ', 1)

    if log_type == 'START':
        # regex para encontrar todos os pares chave-valor na string de log
        # no caso do START, o separador das chaves é um espaço em branco
        key_value_pairs = re.findall(r'(\w+): ([^\s]+)', log_details)
    else:
        # regex para encontrar todos os pares chave-valor na string de log
        # no caso de outros tipos de log, o separador das chaves é um '\t'
        key_value_pairs = re.findall(r'([\w\s]+): ([^\t\n]+)', log_details)
        # Limpar as chaves removendo qualquer coisa até o último '\t' e espaços em branco no início e no final
        key_value_pairs = [(k.split('\t')[-1].strip(), v) for k, v in key_value_pairs]
    
    if log_type == 'REPORT':
        # adicionar a chave 'Init Duration' com valor None para os logs do tipo REPORT
        # caso não possua essa informação no log
        if not any(k == 'Init Duration' for k, v in key_value_pairs):
            key_value_pairs.append(('Init Duration', None))
    
    # Converter a lista de tuplas em um dicionário
    log_dict = dict(key_value_pairs)

    # Criar um novo dicionário com 'LogType' como o primeiro item e atualiza com 'log_dict'
    ordered_dict = {'LogType': log_type}
    ordered_dict.update(log_dict)

    return ordered_dict