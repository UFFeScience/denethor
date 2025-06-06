from sqlalchemy.orm import Session
from denethor.core.repository.BaseRepository import BaseRepository
from denethor.core.model.Task import Task

class TaskRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session=session, model=Task)
    
    def get_by_id(self, id: int):
        return self.session.query(self.model).filter_by(task_id=id).first()
    
    def get_by_name(self, name: str):
        return self.session.query(self.model).filter_by(task_type=name).first()
    
    def get_or_create(self, obj: Task):
        if type(obj) != Task:
            raise ValueError("The argument must be a Task object")
        obj_dict = obj.__dict__.copy()
        # obj_dict.pop('execution_statistics', None)
        return super().get_or_create(obj_dict)
