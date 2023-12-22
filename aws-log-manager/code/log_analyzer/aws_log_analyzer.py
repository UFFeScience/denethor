from aws_log_utils import *
from message_analyzer import *

# Define the list of keywords for filtering
keywords = ["RequestId:"]  # Add your keywords here
# keywords = ["INIT", "START", "s3_bucket", "s3_key", "END:", "REPORT"]  # Add your keywords here



with open('aws-log-manager/logs/logs_tree_constructor.json') as f:
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
            
            log_type = re.search('^\\w+', message).group(0)
            match log_type:
                case 'INIT_START':
                    init_start_analyzer(message, log_stream_name, timestamp)

                case 'START':
                    start_analyzer(message)
                
                case 'FILE_DOWNLOAD' | 'FILE_UPLOAD':
                    file_download_analyzer(message)
                
                case 'END':
                    end_analyzer(message)
                
                case 'REPORT':
                    report_analyzer(message)
                
                # Code for invalid log types
                case _:
                    print(f'Invalid Log Type: {log_type}!!!!')

# log_str = json.dumps(log)