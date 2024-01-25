import re
from db.db_model import *
from db.repository import *
from db.conn import *
from utils.log_utils import *


def parse_logs(request_id, logs):
    
    service_executions = []
    execution_files = []
    files = []
    execution_statistics = []
    statistics = []

    se = ServiceExecution(request_id=request_id)
    service_executions.append(se)
    
    for log in logs:
        
        #   
        # Validations of request_id
        #
        curr_request_id = get_request_id(log)
        
        if curr_request_id is None:
            raise ValueError(f"Invalid request_id:{curr_request_id}")
        
        if se.request_id != curr_request_id:
            raise ValueError(f"Error! Current request_id:{curr_request_id} | Expected request_id:{se.request_id}")
        
        ##########


        se.log_stream_name = get_log_stream_name(log)
        
        log_type = get_log_type(log)

        match log_type:
            case 'START':
                process_start(se, log)
            
            case 'END':
                process_end(se, log)
            
            case 'REPORT':
                process_report(se, log)
            
            case 'FILE_DOWNLOAD':
                process_file_info('consumed', message)
            
            case 'FILE_UPLOAD':
                process_file_info('produced', message)
            
            case 'CONSUMED_FILES_INFO':
                process_total_file_info('consumed', message)
            
            case 'PRODUCED_FILES_INFO':
                process_total_file_info('produced', message)
            
            case 'SUBTREE_FILES_CREATE':
                process_subtree_info(message)
            
            case 'MAF_DATABASE_CREATE':
                process_maf_databse_info(message)
            
            case _:
                log_type = None

# "timestamp": 1705599854279, "message": "START RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c Version: $LATEST\n"
def process_start(se, log):
    se.start_time = convert_to_datetime(log['timestamp'])


# "timestamp": 1705599874327, "message": "END RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\n"
def process_end(se, log):
    se.end_time = convert_to_datetime(log['timestamp'])


# "message": "REPORT RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\tDuration: 1010.14 ms\tBilled Duration: 1011 ms\tMemory Size: 128 MB\tMax Memory Used: 115 MB\tInit Duration: 918.52 ms\t\n"
def process_report(se, log):
    se.duration = get_duration(log)
    se.billed_duration = get_billed_duration(log)
    se.memory_size = get_memory_size(log)
    se.max_memory_used = get_max_memory_used(log)
    se.init_duration = get_init_duration(log)


# "message": "FILE_DOWNLOAD RequestId: c3df54b6-1da5-48b2-bec4-093b55c96692\t FileName: ORTHOMCL1\t Bucket: mribeiro-bucket-input\t FilePath: data/testset/ORTHOMCL1\t Duration: 407.83485699999744 ms\t FileSize: 1640 bytes\n"
# "message": "FILE_UPLOAD RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\t FileName: tree_ORTHOMCL1.nexus\t Bucket: mribeiro-bucket-output-tree\t FilePath: tree_ORTHOMCL1.nexus\t Duration: 292.6312569999965\t FileSize: 339\n"
def process_file_info(action_type: str, message):
    file_info.append({
        'name': re.search('FileName: (.+?)\\t', message).group(1),
        'size': re.search('FileSize: (.+?) bytes\\n', message).group(1),
        'path': re.search('FilePath: (.+?)\\t', message).group(1),
        'bucket': re.search('Bucket: (.+?)\\t', message).group(1),
        'transfer_duration': re.search('Duration: (.+?) ms\\t', message).group(1),
        'action_type': action_type
    })

# "message": "CONSUMED_FILES_INFO RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t NumFiles: 100 files\t TotalFilesSize: 36777 bytes\t Duration: 6933.13087699994 ms\n"
# "message": "PRODUCED_FILES_INFO RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t NumFiles: 335 files\t TotalFilesSize: 83697 bytes\t Duration: 17168.395734999875 ms\n"
def process_total_file_info(action_type: str, message):
    execution_info[f'num_{action_type}_files'] = re.search('NumFiles: (.+?) files\\t', message).group(1)
    execution_info[f'total_{action_type}_files_size'] = re.search('TotalFilesSize: (.+?) bytes\\t', message).group(1)
    execution_info[f'total_{action_type}_transfer_duration'] = re.search('Duration: (.+?) ms\\n', message).group(1)
    

# "message": "SUBTREE_FILES_CREATE RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t Duration: 795.8109850000028 ms\n"
def process_subtree_info(message):
    other_stats_info['subtree_duration'] = re.search('Duration: (.+?) ms\\n', message).group(1)


# "message": "MAF_DATABASE_CREATE RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t MaxMaf: 5\t Duration: 485681.23013399995 ms\t MafDatabase: {1: {}, 2: {'tree_ORTHOMCL1_Inner3.nexus': ['tree_ORTHOMCL1977_Inner2.nexus', 'tree_ORTHOMCL1977_Inner1.nexus'],      (.......)     , 3: {}, 5: {'tree_ORTHOMCL1_Inner3.nexus': ['tree_ORTHOMCL1977_Inner3.nexus'],) 'tree_ORTHOMCL1977_Inner3.nexus': ['tree_ORTHOMCL1_Inner3.nexus']}}\n"
def process_maf_databse_info(message):
    other_stats_info['max_maf'] = re.search('MaxMaf: (.+?)\\t', message).group(1)
    other_stats_info['maf_db_duration'] = re.search('Duration: (.+?) ms\\t', message).group(1)
    other_stats_info['maf_database'] = re.search('MafDatabase: (.+?)\\n', message).group(1)


