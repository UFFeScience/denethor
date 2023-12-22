from log_model import LogModel
import re

class MessageAnalyzer:
    def __init__(self):
        self.log_model = LogModel("log_stream_name")

    def process_request_id(self, request_id):
        self.log_model.request_id = request_id



    # "INIT_START Runtime Version: python:3.11.v18\tRuntime Version ARN: arn:aws:lambda:sa-east-1::runtime:6ebff6b58cf714d30879a40cc31554cd1bbc242da7bf75a000bc0c3052c6ebbc\n"
    def init_start_analyzer(self, log):
        message = log.get('message')
        timestamp = log.get('timestamp')
        
        self.log_model.runtime_version = re.search('Runtime Version: (.+?)\\t', message).group(1)
        self.log_model.runtime_version_arn = re.search('Runtime Version ARN: (.+?)\n', message).group(1)

    # "START RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c Version: $LATEST\n"
    def start_analyzer(self, log):
        message = log.get('message')
        self.log_model.request_id = re.search('RequestId: (.+?)\\s', message).group(1)
        self.log_model.version = re.search('Version: (.+?)\\n', message).group(1)


# "FILE_DOWNLOAD RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\t FileName: ORTHOMCL1\t Bucket: mribeiro-bucket-input\t FilePath: data/testset/ORTHOMCL1\t Duration: 415.46021699999613\t FileSize: 1640\n"
# "FILE_UPLOAD RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\t FileName: tree_ORTHOMCL1.nexus\t Bucket: mribeiro-bucket-output-tree\t FilePath: tree_ORTHOMCL1.nexus\t Duration: 292.6312569999965\t FileSize: 339\n"
def file_download_analyzer(message):
    self.log_model.log_type = re.search('^\\w+', message).group(0)
    self.log_model.request_id = re.search('RequestId: (.+?)\\s', message).group(1)
    self.log_model.file_name = re.search('FileName: (.+?)\\t', message).group(1)
    self.log_model.bucket = re.search('Bucket: (.+?)\\t', message).group(1)
    self.log_model.file_path = re.search('FilePath: (.+?)\\t', message).group(1)
    self.log_model.duration = re.search('Duration: (.+?)\\t', message).group(1)
    self.log_model.file_size = re.search('FileSize: (.+?)$', message).group(1)


# "END RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\n"
def end_analyzer(message):
    self.log_model.request_id = re.search('RequestId: (.+?)\\s', message).group(1)


# "REPORT RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\tDuration: 1010.14 ms\tBilled Duration: 1011 ms\tMemory Size: 128 MB\tMax Memory Used: 115 MB\tInit Duration: 918.52 ms\t\n"
def report_analyzer(message, timestamp):
    self.log_model.request_id = re.search('RequestId: (.+?)\\s', message).group(1)
    self.log_model.duration = re.search('Duration: (.+?) ms\\t', message).group(1)
    self.log_model.billed_duration = re.search('Billed Duration: (.+?) ms\\t', message).group(1)
    self.log_model.memory_size = re.search('Memory Size: (.+?) MB\\t', message).group(1)
    self.log_model.max_memory_used = re.search('Max Memory Used: (.+?) MB\\t', message).group(1)
    
    # Verificar se o atributo "Init Duration" existe
    init_duration_match = re.search('Init Duration: (.+?) ms\\t', message)
    if init_duration_match != None:
       self.log_model.init_duration = init_duration_match.group(1)
    