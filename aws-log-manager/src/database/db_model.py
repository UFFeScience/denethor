from sqlalchemy import Column, Integer, String, Float, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    @classmethod
    def create_from_dict(cls, dict_values):
        filtered_dict = {k: v for k, v in dict_values.items() if hasattr(cls, k)}
        return cls(**filtered_dict)

    def update_from_dict(self, dict_values):
        filtered_dict = {k: v for k, v in dict_values.items() if hasattr(self, k)}
        for key, value in filtered_dict.items():
            setattr(self, key, value)

            
# Este método cria todas as tabelas armazenadas na metadata no banco de dados conectado ao engine. As tabelas são criadas no banco de dados usando o engine fornecido. Se uma tabela já existe no banco de dados, o método create_all() irá ignorá-la.
# Base.metadata.create_all(engine)

class ServiceProvider(BaseModel):
    __tablename__ = 'service_provider'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    memory = Column(Integer)
    timeout = Column(Integer)
    cpu = Column(Integer)

    def __str__(self):
        return (f"[{self.id}]={self.name}, {self.memory}MB, {self.timeout}s, {self.cpu}vCPU")

class Workflow(BaseModel):
    __tablename__ = 'workflow'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    def __str__(self):
        return (f"[{self.id}]={self.name}")


class WorkflowActivity(BaseModel):
    __tablename__ = 'workflow_activity'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    workflow_id = Column(Integer, ForeignKey('workflow.id'))

    def __str__(self):
        return (f"[{self.id}]={self.name}")

class ServiceExecution(BaseModel):
    __tablename__ = 'service_execution'

    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey('workflow_activity.id'))
    service_id = Column(Integer, ForeignKey('service_provider.id'))
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
    produced_files_count = Column(Integer)
    consumed_files_size = Column(Integer)
    produced_files_size = Column(Integer)
    consumed_files_transfer_duration = Column(Float)
    produced_files_transfer_duration = Column(Float)
    error_message = Column(String)

    execution_files = relationship('ExecutionFile')
    execution_statistics = relationship('ExecutionStatistics')
    activity = relationship('WorkflowActivity')
    service = relationship('ServiceProvider')

    def __str__(self):
        return (
            f"Id: {self.id}\n"
            f"Activity ID: {self.activity_id}\n"
            f"Service ID: {self.service_id}\n"
            f"Request ID: {self.request_id}\n"
            f"Log Stream Name: {self.log_stream_name}\n"
            f"Start Time: {self.start_time}\n"
            f"End Time: {self.end_time}\n"
            f"Duration: {self.duration}\n"
            f"Billed Duration: {self.billed_duration}\n"
            f"Init Duration: {self.init_duration}\n"
            f"Memory Size: {self.memory_size}\n"
            f"Max Memory Used: {self.max_memory_used}\n"
            f"Num Consumed Files: {self.consumed_files_count}\n"
            f"Num Produced Files: {self.produced_files_count}\n"
            f"Total Consumed Files Size: {self.consumed_files_size}\n"
            f"Total Produced Files Size: {self.produced_files_size}\n"
            f"Total Consumed Transfer Duration: {self.consumed_files_transfer_duration}\n"
            f"Total Produced Transfer Duration: {self.produced_files_transfer_duration}\n"
            f"Error Message: {self.error_message}\n"
        )


class File(BaseModel):
    __tablename__ = 'file'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    bucket = Column(String)
    path = Column(String)
    size = Column(Float)

    def __str__(self):
        return (f"[{self.id}]={self.name} ({self.size} bytes)")


class ExecutionFile(BaseModel):
    __tablename__ = 'execution_file'

    id = Column(Integer, primary_key=True)
    service_execution_id = Column(Integer, ForeignKey('service_execution.id'))
    file_id = Column(Integer, ForeignKey('file.id'))
    transfer_duration = Column(Float)
    transfer_type = Column(String)

    file = relationship("File", backref="execution_file")
    service_execution = relationship("ServiceExecution")

    def __str__(self):
        return (f"[{self.id}]={self.transfer_duration} ms ({self.transfer_type})")
    
    
class Statistics(BaseModel):
    __tablename__ = 'statistics'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    
    def __str__(self):
        return (f"[{self.id}]={self.name}")

class ExecutionStatistics(BaseModel):
    __tablename__ = 'execution_statistics'

    id = Column(Integer, primary_key=True)
    service_execution_id = Column(Integer, ForeignKey('service_execution.id'))
    statistics_id = Column(Integer, ForeignKey('statistics.id'))
    value_float = Column(Float)
    value_integer = Column(Integer)
    value_string = Column(String)

    statistics = relationship("Statistics", backref="execution_statistics")
    service_execution = relationship("ServiceExecution")

    def __str__(self):
        if self.value_float is not None:
            return str(self.value_float)
        elif self.value_integer is not None:
            return str(self.value_integer)
        elif self.value_string is not None:
            return str(self.value_string)
        else:
            return ''