from aws_log_utils import *

# Define the list of keywords for filtering
keywords = ["RequestId:"]  # Add your keywords here
# keywords = ["INIT", "START", "s3_bucket", "s3_key", "END:", "REPORT"]  # Add your keywords here



with open('logs_tree_constructor.json') as f:
    data = f.readlines()

log_stream_dict = {}

for line in data:
    item = json.loads(line)
    log_stream_name = item['logStreamName']
    if log_stream_name not in log_stream_dict:
        log_stream_dict[log_stream_name] = []
    log_stream_dict[log_stream_name].append(item)

# print(log_stream_dict)

# print_logs_to_console(log_stream_dict)

# Filter logs by keywords
# filtered_logs = filter_logs_by_keywords(log_stream_dict, keywords)
# print_logs_to_console(filtered_logs)

for log_stream_name, logs in log_stream_dict.items():
        for log in logs:
            message = log.get('message')
            log_type = re.search('^\\w+', message).group(0)
            match log_type:
                # "INIT_START Runtime Version: python:3.11.v18\tRuntime Version ARN: arn:aws:lambda:sa-east-1::runtime:6ebff6b58cf714d30879a40cc31554cd1bbc242da7bf75a000bc0c3052c6ebbc\n"
                case 'INIT_START':
                    runtime_version = re.search('Runtime Version: (.+?)\\t', message).group(1)
                    runtime_version_arn = re.search('Runtime Version ARN: (.+?)\n', message).group(1)
                    print("-" * 80)
                    print(f'Log Type: {log_type}')
                    print(f'Runtime Version: {runtime_version}')
                    print(f'Runtime Version ARN: {runtime_version_arn}')

                # "START RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c Version: $LATEST\n"
                case 'START':
                    request_id = re.search('RequestId: (.+?)\\s', message).group(1)
                    version = re.search('Version: (.+?)\\n', message).group(1)
                    print("-" * 80)
                    print(f'Log Type: {log_type}')
                    print(f'RequestId: {request_id}')
                    print(f'Version: {version}')
                
                # "FILE_DOWNLOAD RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\t FileName: ORTHOMCL1\t Bucket: mribeiro-bucket-input\t FilePath: data/testset/ORTHOMCL1\t Duration: 415.46021699999613\t FileSize: 1640\n"
                # "FILE_UPLOAD RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\t FileName: tree_ORTHOMCL1.nexus\t Bucket: mribeiro-bucket-output-tree\t FilePath: tree_ORTHOMCL1.nexus\t Duration: 292.6312569999965\t FileSize: 339\n"
                case 'FILE_DOWNLOAD' | 'FILE_UPLOAD':
                    request_id = re.search('RequestId: (.+?)\\s', message).group(1)
                    file_name = re.search('FileName: (.+?)\\t', message).group(1)
                    bucket = re.search('Bucket: (.+?)\\t', message).group(1)
                    file_path = re.search('FilePath: (.+?)\\t', message).group(1)
                    duration = re.search('Duration: (.+?)\\t', message).group(1)
                    file_size = re.search('FileSize: (.+?)$', message).group(1)
                    print("-" * 80)
                    print(f'Log Type: {log_type}')
                    print(f'RequestId: {request_id}')
                    print(f'FileName: {file_name}')
                    print(f'Bucket: {bucket}')
                    print(f'FilePath: {file_path}')
                    print(f'Duration: {duration}')
                    print(f'FileSize: {file_size}')

                # "END RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\n"
                case 'END':
                    request_id = re.search('RequestId: (.+?)\\s', message).group(1)
                    print("-" * 80)
                    print(f'Log Type: {log_type}')
                    print(f'RequestId: {request_id}')
                
                # "REPORT RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\tDuration: 1010.14 ms\tBilled Duration: 1011 ms\tMemory Size: 128 MB\tMax Memory Used: 115 MB\tInit Duration: 918.52 ms\t\n"
                case 'REPORT':
                    request_id = re.search('RequestId: (.+?)\\s', message).group(1)
                    duration = re.search('Duration: (.+?) ms\\t', message).group(1)
                    billed_duration = re.search('Billed Duration: (.+?) ms\\t', message).group(1)
                    memory_size = re.search('Memory Size: (.+?) MB\\t', message).group(1)
                    max_memory_used = re.search('Max Memory Used: (.+?) MB\\t', message).group(1)
                    
                    # Verificar se o atributo "Init Duration" existe
                    init_duration_match = re.search('Init Duration: (.+?) ms\\t', message)
                    init_duration = 0
                    if init_duration_match != None:
                        init_duration = init_duration_match.group(1)
                    
                    print("-" * 80)
                    print(f'Log Type: {log_type}')
                    print(f'RequestId: {request_id}')
                    print(f'Duration: {duration} ms')
                    print(f'Billed Duration: {billed_duration} ms')
                    print(f'Memory Size: {memory_size} MB')
                    print(f'Max Memory Used: {max_memory_used} MB')
                    print(f'Init Duration: {init_duration} ms')
                
                # Code for invalid log types
                #case _:
                    #print(f'Invalid Log Type: {log_type}!!!!')

# log_str = json.dumps(log)