from datetime import datetime, timezone
import re

class RequestLogModel:
    
    def __init__(self, request_id):
        
        if request_id == None:
            raise ValueError("Invalid request_id:{request_id}")
        
        self.request_id = request_id

        # START
        self.startTime = None
        
        # FILE_DOWNLOAD
        self.download_file_name = None
        self.download_bucket = None
        self.download_file_path = None
        self.download_duration = None
        self.download_file_size = None

        # FILE_UPLOAD
        self.upload_file_name = None
        self.upload_bucket = None
        self.upload_file_path = None
        self.upload_duration = None
        self.upload_file_size = None

        # END
        self.endTime = None

        # REPORT
        self.duration = None
        self.billed_duration = None
        self.memory_size = None
        self.max_memory_used = None
        self.init_duration = None

    
    def print(self):
        print(f"---------------------------------")
        for key, value in vars(self).items():
            print(f"{key}: {value}".strip())
        print(f"---------------------------------\n")


    def process(self, log_item):
        
        timestamp = log_item.get('timestamp')
        message = log_item.get('message')
        request_id = re.search('RequestId: (.+?)\\s', message).group(1)

        # Validations of request_id
        if request_id == None:
            raise ValueError("Invalid request_id:{request_id}")
        elif self.request_id != request_id:
            raise ValueError("Error! New request_id:{request_id} | Expected request_id:{self.request_id}")

        log_type = re.search('^\\w+', message).group(0)

        match log_type:
            case 'START':
                self.process_start(timestamp)
            
            case 'FILE_DOWNLOAD':
                self.process_file_download(message)
           
            case 'FILE_UPLOAD':
                self.process_file_upload(message)
           
            case 'REPORT':
                self.process_report(message)
            
            case 'END':
                self.process_end(timestamp)
            
            case _:
                log_type = None

    
    # "START RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c Version: $LATEST\n"
    def process_start(self, timestamp):
        self.startTime = timestamp

    # "FILE_DOWNLOAD RequestId: c3df54b6-1da5-48b2-bec4-093b55c96692\t FileName: ORTHOMCL1\t Bucket: mribeiro-bucket-input\t FilePath: data/testset/ORTHOMCL1\t Duration: 407.83485699999744 ms\t FileSize: 1640 bytes\n"
    def process_file_download(self, message):
        self.download_file_name = re.search('FileName: (.+?)\\t', message).group(1)
        self.download_bucket = re.search('Bucket: (.+?)\\t', message).group(1)
        self.download_file_path = re.search('FilePath: (.+?)\\t', message).group(1)
        self.download_duration = re.search('Duration: (.+?) ms\\t', message).group(1)
        self.download_file_size = re.search('FileSize: (.+?)\s', message).group(1)

    # "FILE_UPLOAD RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\t FileName: tree_ORTHOMCL1.nexus\t Bucket: mribeiro-bucket-output-tree\t FilePath: tree_ORTHOMCL1.nexus\t Duration: 292.6312569999965\t FileSize: 339\n"
    def process_file_upload(self, message):
        self.upload_file_name = re.search('FileName: (.+?)\\t', message).group(1)
        self.upload_bucket = re.search('Bucket: (.+?)\\t', message).group(1)
        self.upload_file_path = re.search('FilePath: (.+?)\\t', message).group(1)
        self.upload_duration = re.search('Duration: (.+?) ms\\t', message).group(1)
        self.upload_file_size = re.search('FileSize: (.+?)\s', message).group(1)
    
    # "REPORT RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\tDuration: 1010.14 ms\tBilled Duration: 1011 ms\tMemory Size: 128 MB\tMax Memory Used: 115 MB\tInit Duration: 918.52 ms\t\n"
    def process_report(self, message):
        self.duration = re.search('Duration: (.+?) ms\\t', message).group(1)
        self.billed_duration = re.search('Billed Duration: (.+?) ms\\t', message).group(1)
        self.memory_size = re.search('Memory Size: (.+?) MB\\t', message).group(1)
        self.max_memory_used = re.search('Max Memory Used: (.+?) MB\\t', message).group(1)
        # Verificar se o atributo "Init Duration" existe
        init_duration_match = re.search('Init Duration: (.+?) ms\\t', message)
        if init_duration_match != None:
            self.init_duration = init_duration_match.group(1)
    
    # "END RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\n"
    def process_end(self, timestamp):
        self.endTime = timestamp

    # Create datetime objects (in UTC) from the timestamps in milliseconds
    def start_time_date(self):
        if self.startTime:
            return datetime.fromtimestamp((self.startTime / 1000.0), tz=timezone.utc)
        return None
    
    # Create datetime objects (in UTC) from the timestamps in milliseconds 
    def end_time_date(self):
        if self.endTime:
            return datetime.fromtimestamp((self.endTime / 1000.0), tz=timezone.utc)
        return None