class RequestLog:
    
    def __init__(self, log_stream_name):
        
        self.log_stream_name = log_stream_name

        # # INIT_START
        # self.runtime_version = None
        # self.runtime_version_arn = None
        
        # START
        self.request_id = None
        self.startTime = None
        self.version = None
        
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
        for key, value in vars(self).items():
            print(f"{key}: {value}")