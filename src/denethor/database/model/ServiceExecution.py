from denethor.database.model.BaseModel import *

class ServiceExecution(BaseModel):
    __tablename__ = 'service_execution'

    se_id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey('workflow_activity.activity_id'))
    provider_id = Column(Integer, ForeignKey('provider.provider_id'))
    configuration_id = Column(Integer, ForeignKey('provider_configuration.configuration_id'))
    workflow_execution_id = Column(String)
    request_id = Column(String)
    log_stream_name = Column(String)
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)
    duration = Column(Float)
    billed_duration = Column(Float)
    init_duration = Column(Float)
    memory_size = Column(Integer)
    max_memory_used = Column(Integer)
    consumed_files_count = Column(Integer)
    consumed_files_size = Column(Integer)
    consumed_files_transfer_duration = Column(Float)
    produced_files_count = Column(Integer)
    produced_files_size = Column(Integer)
    produced_files_transfer_duration = Column(Float)
    error_message = Column(String)

    execution_files = relationship('ExecutionFile')
    execution_statistics = relationship('ExecutionStatistics')
    activity = relationship('WorkflowActivity')
    provider = relationship('Provider')
    provider_configuration = relationship('ProviderConfiguration')

    def __str__(self):
        return (
            f"Id: {self.se_id}\n"
            f"Activity ID: {self.activity_id}\n"
            f"Provider ID: {self.provider_id}\n"
            f"Configuration ID: {self.configuration_id}\n"
            f"Workflow Execution ID: {self.workflow_execution_id}\n"
            f"Request ID: {self.request_id}\n"
            f"Log Stream Name: {self.log_stream_name}\n"
            f"Start Time: {self.start_time}\n"
            f"End Time: {self.end_time}\n"
            f"Duration: {self.duration}\n"
            f"Billed Duration: {self.billed_duration}\n"
            f"Init Duration: {self.init_duration}\n"
            f"Memory Size: {self.memory_size}\n"
            f"Max Memory Used: {self.max_memory_used}\n"
            f"Consumed Files Count: {self.consumed_files_count}\n"
            f"Consumed Files Size: {self.consumed_files_size}\n"
            f"Consumed Transfer Duration: {self.consumed_files_transfer_duration}\n"
            f"Produced Files Count: {self.produced_files_count}\n"
            f"Produced Files Size: {self.produced_files_size}\n"
            f"Produced Transfer Duration: {self.produced_files_transfer_duration}\n"
            f"Error Message: {self.error_message}\n"
        )