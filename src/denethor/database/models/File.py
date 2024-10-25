from denethor.database.models.BaseModel import *

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