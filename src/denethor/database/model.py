from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, Text, UniqueConstraint
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
        # Certifique-se de que dict_values é um dicionário
        if not isinstance(dict_values, dict):
            raise TypeError("dict_values deve ser um dicionário")
        
        # Filtre apenas os atributos que pertencem à classe cls
        filtered_dict = {k: v for k, v in dict_values.items() if hasattr(cls, k)}
        
        if not filtered_dict or len(filtered_dict) == 0:
            raise ValueError("No attributes found in the dictionary that belong to the class")
        
        # Crie uma instância da classe com os atributos filtrados
        return cls(**filtered_dict)

    def update_from_dict(self, dict_values):
        filtered_dict = {k: v for k, v in dict_values.items() if hasattr(self, k)}
        for key, value in filtered_dict.items():
            setattr(self, key, value)

            
# Este método cria todas as tabelas armazenadas na metadata no banco de dados conectado ao engine. As tabelas são criadas no banco de dados usando o engine fornecido. Se uma tabela já existe no banco de dados, o método create_all() irá ignorá-la.
# Base.metadata.create_all(engine)

class Provider(BaseModel):
    __tablename__ = 'provider'

    provider_id = Column(Integer, primary_key=True)
    provider_name = Column(String)

    # configurations = relationship("ProviderConfiguration", backref="provider")

    def __str__(self):
        return f"[{self.provider_id}] {self.provider_name}"


class ProviderConfiguration(BaseModel):
    __tablename__ = 'provider_configuration'

    configuration_id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey('provider.provider_id'))
    timeout = Column(Integer)
    cpu = Column(Integer)
    memory_mb = Column(Integer)
    storage_mb = Column(Integer)

    provider = relationship("Provider")

    def __str__(self):
        return (f"[{self.configuration_id}], {self.memory_mb}MB RAM, "
                f"{self.timeout}s timeout, {self.cpu}vCPU, {self.storage_mb}MB storage")


class Workflow(BaseModel):
    __tablename__ = 'workflow'

    workflow_id = Column(Integer, primary_key=True)
    workflow_name = Column(String)
    workflow_description = Column(String)

    def __str__(self):
        return (f"[{self.workflow_id}]={self.workflow_name}")


class WorkflowActivity(BaseModel):
    __tablename__ = 'workflow_activity'

    activity_id = Column(Integer, primary_key=True)
    activity_name = Column(String)
    activity_description = Column(String)
    workflow_id = Column(Integer, ForeignKey('workflow.workflow_id'))

    workflow = relationship('Workflow')
    tasks = relationship("Task", back_populates="activity")

    def __str__(self):
        return (f"[{self.activity_id}]={self.activity_name}")



class Task(Base):
    __tablename__ = 'task'
    
    task_id = Column(Integer, primary_key=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey('workflow_activity.activity_id'), nullable=False)
    task_type = Column(Integer, nullable=False)
    input_count = Column(Text, nullable=False)
    input_list = Column(Text, nullable=False)
    output_count = Column(Text, nullable=False)
    output_list = Column(Text, nullable=False)

    # Define relationships if needed
    activity = relationship("WorkflowActivity", back_populates="tasks")



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
    configuration = relationship('ProviderConfiguration')

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


class File(BaseModel):
    __tablename__ = 'file'

    file_id = Column(Integer, primary_key=True)
    file_name = Column(String, unique=True)
    file_bucket = Column(String)
    file_path = Column(String)
    file_size = Column(Float)
    file_hash_code = Column(String)

    task_files = relationship("TaskFile", back_populates="file")    
    
    def __str__(self):
        return (f"[{self.file_id}]={self.file_name} ({self.file_size} bytes)")


class ExecutionFile(BaseModel):
    __tablename__ = 'execution_file'

    ef_id = Column(Integer, primary_key=True)
    se_id = Column(Integer, ForeignKey('service_execution.se_id'))
    file_id = Column(Integer, ForeignKey('file.file_id'))
    transfer_duration = Column(Float)
    transfer_type = Column(String)

    file = relationship("File", backref="execution_file")
    service_execution = relationship("ServiceExecution")

    def __str__(self):
        return (f"[{self.ef_id}]={self.transfer_duration} ms ({self.transfer_type})")
    
    
class Statistics(BaseModel):
    __tablename__ = 'statistics'

    statistics_id = Column(Integer, primary_key=True)
    statistics_name = Column(String)
    statistics_description = Column(String)
    
    def __str__(self):
        return (f"[{self.statistics_id}]={self.statistics_name}")

class ExecutionStatistics(BaseModel):
    __tablename__ = 'execution_statistics'

    es_id = Column(Integer, primary_key=True)
    se_id = Column(Integer, ForeignKey('service_execution.se_id'))
    statistics_id = Column(Integer, ForeignKey('statistics.statistics_id'))
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
        