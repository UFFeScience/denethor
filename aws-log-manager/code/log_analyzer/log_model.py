class LogModel:
    def __init__(self, log_stream_name):
        self.log_stream_name = log_stream_name
        self.runtime_version = None
        self.request_id = None
        self.version = None
        
        self.download_file_name = None
        self.download_bucket = None
        self.download_file_path = None
        self.download_duration = None
        self.download_file_size = None

        self.upload_file_name = None
        self.upload_bucket = None
        self.upload_file_path = None
        self.upload_duration = None
        self.upload_file_size = None

        self.duration = None
        self.billed_duration = None
        self.init_duration = None
        self.memory_size = None
        self.max_memory_used = None

        self.startTime = None
        self.endTime = None