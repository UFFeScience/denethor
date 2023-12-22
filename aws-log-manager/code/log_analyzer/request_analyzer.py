from request_log import RequestLog
import re

class RequestAnalyzer:
    
    def __init__(self, log_stream_name):
        self.request_log = RequestLog(log_stream_name)
        
    
    def process_log(self, log):
        self.log = log
        message = self.log.get('message')
        log_type = re.search('^\\w+', message).group(0)
        
        match log_type:
            case 'INIT_START':
                self.process_init_start(message)

            case 'START':
                self.process_start(message)
            
            case 'FILE_DOWNLOAD':
                self.process_file_download(message)
            
            case 'FILE_UPLOAD':
                self.process_file_upload(message)
            
            case 'END':
                self.process_end(message)
            
            case 'REPORT':
                self.process_report(message)
            

    # "INIT_START Runtime Version: python:3.11.v18\tRuntime Version ARN: arn:aws:lambda:sa-east-1::runtime:6ebff6b58cf714d30879a40cc31554cd1bbc242da7bf75a000bc0c3052c6ebbc\n"
    def process_init_start(self, message):
        self.request_log.startTime = self.log.get('timestamp')
        self.request_log.runtime_version = re.search('Runtime Version: (.+?)\\t', message).group(1)
        self.request_log.runtime_version_arn = re.search('Runtime Version ARN: (.+?)\n', message).group(1)


    # "START RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c Version: $LATEST\n"
    def process_start(self, message):
        self.request_log.request_id = re.search('RequestId: (.+?)\\s', message).group(1)
        self.request_log.version = re.search('Version: (.+?)\\n', message).group(1)


    # "FILE_DOWNLOAD RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\t FileName: ORTHOMCL1\t Bucket: mribeiro-bucket-input\t FilePath: data/testset/ORTHOMCL1\t Duration: 415.46021699999613\t FileSize: 1640\n"
    def process_file_download(self, message):
        self.request_log.download_file_name = re.search('FileName: (.+?)\\t', message).group(1)
        self.request_log.download_bucket = re.search('Bucket: (.+?)\\t', message).group(1)
        self.request_log.download_file_path = re.search('FilePath: (.+?)\\t', message).group(1)
        self.request_log.download_duration = re.search('Duration: (.+?)\\t', message).group(1)
        self.request_log.download_file_size = re.search('FileSize: (.+?)$', message).group(1)

    # "FILE_UPLOAD RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\t FileName: tree_ORTHOMCL1.nexus\t Bucket: mribeiro-bucket-output-tree\t FilePath: tree_ORTHOMCL1.nexus\t Duration: 292.6312569999965\t FileSize: 339\n"
    def process_file_upload(self, message):
        self.request_log.upload_file_name = re.search('FileName: (.+?)\\t', message).group(1)
        self.request_log.upload_bucket = re.search('Bucket: (.+?)\\t', message).group(1)
        self.request_log.upload_file_path = re.search('FilePath: (.+?)\\t', message).group(1)
        self.request_log.upload_duration = re.search('Duration: (.+?)\\t', message).group(1)
        self.request_log.upload_file_size = re.search('FileSize: (.+?)$', message).group(1)


    # "END RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\n"
    def process_end(self, message):
        self.request_log.endTime = self.log.get('timestamp')

    # "REPORT RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\tDuration: 1010.14 ms\tBilled Duration: 1011 ms\tMemory Size: 128 MB\tMax Memory Used: 115 MB\tInit Duration: 918.52 ms\t\n"
    def process_report(self, message):
        self.request_log.duration = re.search('Duration: (.+?) ms\\t', message).group(1)
        self.request_log.billed_duration = re.search('Billed Duration: (.+?) ms\\t', message).group(1)
        self.request_log.memory_size = re.search('Memory Size: (.+?) MB\\t', message).group(1)
        self.request_log.max_memory_used = re.search('Max Memory Used: (.+?) MB\\t', message).group(1)
        
        # Verificar se o atributo "Init Duration" existe
        init_duration_match = re.search('Init Duration: (.+?) ms\\t', message)
        if init_duration_match != None:
            self.request_log.init_duration = init_duration_match.group(1)
