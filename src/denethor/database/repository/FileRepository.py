from sqlalchemy.orm import Session
from denethor.database.repository.BaseRepository import BaseRepository
from denethor.database.models.File import File

class FileRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session=session, model=File)
    
    def get_by_id(self, id: int):
        return self.db.query(self.model).filter_by(file_id=id).first()
    
    def get_or_create(self, obj: File):
        if type(obj) != File:
            raise ValueError("The argument must be a File object")
        obj_dict = obj.__dict__.copy()
        obj_dict.pop('execution_file', None)
        return super().get_or_create(obj_dict)