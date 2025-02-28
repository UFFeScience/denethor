from sqlalchemy.orm import Session
from denethor.database.repository.BaseRepository import BaseRepository
from denethor.database.model.ExecutionFile import ExecutionFile

class ExecutionFileRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session=session, model=ExecutionFile)

    def get_by_id(self, id: int):
        return self.db.query(self.model).filter_by(ef_id=id).first()
    
    def get_or_create(self, obj: ExecutionFile):
        if type(obj) != ExecutionFile:
            raise ValueError("The argument must be an ExecutionFile object")
        if obj.file:
            obj.file_id = obj.file.file_id
        if obj.service_execution:  
            obj.se_id = obj.service_execution.se_id
        obj_dict = obj.__dict__.copy()
        obj_dict.pop('file', None)
        obj_dict.pop('service_execution', None)
        return super().get_or_create(obj_dict)