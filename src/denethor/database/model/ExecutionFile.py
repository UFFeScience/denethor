from denethor.database.model.BaseModel import *

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
