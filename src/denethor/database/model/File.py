from denethor.database.model.BaseModel import *

class File(BaseModel):
    __tablename__ = 'file'

    file_id = Column(Integer, primary_key=True)
    file_name = Column(String, nullable=False)
    file_bucket = Column(String)
    file_path = Column(String)
    file_size = Column(Float, nullable=False)
    file_hash_code = Column(String, nullable=False)

    def __str__(self):
        return (f"[{self.file_id}]={self.file_name} ({self.file_size} bytes)")