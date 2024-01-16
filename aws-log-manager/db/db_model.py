from sqlalchemy import Column, Integer, String, Float, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ServiceProvider(Base):
    __tablename__ = 'service_provider'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    memory = Column(Integer)
    timeout = Column(Integer)
    cpu = Column(Integer)

class Workflow(Base):
    __tablename__ = 'workflow'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)


class WorkflowActivity(Base):
    __tablename__ = 'workflow_activity'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    workflow_id = Column(Integer, ForeignKey('workflow.id'))


class File(Base):
    __tablename__ = 'file'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    size = Column(Float)
    path = Column(String)
    bucket = Column(String)

    def __str__(self):
        return (f"[{self.id}]={self.name} ({self.size} bytes)")
    
    
class ServiceExecution(Base):
    __tablename__ = 'service_execution'

    id = Column(Integer, primary_key=True)
    request_id = Column(String)
    log_stream_name = Column(String)
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)
    duration = Column(Float)
    billed_duration = Column(Float)
    init_duration = Column(Float)
    consumed_file_download_duration = Column(Float)
    produced_file_upload_duration = Column(Float)
    memory_size = Column(Integer)
    max_memory_used = Column(Integer)
    error_message = Column(String)
    activity_id = Column(Integer, ForeignKey('workflow_activity.id'))
    service_id = Column(Integer, ForeignKey('service_provider.id'))
    consumed_file_id = Column(Integer, ForeignKey('file.id'))
    produced_file_id = Column(Integer, ForeignKey('file.id'))

    def __str__(self):
        return (
            f"Id: {self.id}\n"
            f"Request ID: {self.request_id}\n"
            f"Log Stream Name: {self.log_stream_name}\n"
            f"Start Time: {self.start_time}\n"
            f"End Time: {self.end_time}\n"
            f"Duration: {self.duration}\n"
            f"Billed Duration: {self.billed_duration}\n"
            f"Init Duration: {self.init_duration}\n"
            f"Consumed File Duration: {self.consumed_file_duration}\n"
            f"Produced File Duration: {self.produced_file_duration}\n"
            f"Memory Size: {self.memory_size}\n"
            f"Max Memory Used: {self.max_memory_used}\n"
            f"Error Message: {self.error_message}\n"
            f"Activity ID: {self.activity_id}\n"
            f"Service ID: {self.service_id}\n"
            f"Consumed File ID: {self.consumed_file_id}\n"
            f"Produced File ID: {self.produced_file_id}"
        )

class Statistics(Base):
    __tablename__ = 'statistics'

    id = Column(Integer, primary_key=True)
    name = Column(String)

class ExecutionStatistics(Base):
    __tablename__ = 'execution_statistics'

    id = Column(Integer, primary_key=True)
    value_float = Column(Float)
    value_integer = Column(Integer)
    value_string = Column(String)
    service_execution_id = Column(Integer, ForeignKey('service_execution.id'))
    statistics_id = Column(Integer, ForeignKey('statistics.id'))