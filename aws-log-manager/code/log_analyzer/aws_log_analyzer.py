from aws_log_utils import *
from request_analyzer import *

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
    
    request_analyzer = RequestAnalyzer(log_stream_name)
    
    for log in logs:
        request_analyzer.process_log(log)
    
    request_analyzer.request_log.print()

    # request_analyzer.save_to_database()

# log_str = json.dumps(log)