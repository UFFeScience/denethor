from sqlalchemy.orm import Session
from denethor.database.repository.BaseRepository import BaseRepository
from denethor.database.model.Workflow import Workflow

class WorkflowRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session=session, model=Workflow)
    
    def get_by_id(self, id: int):
        return self.db.query(self.model).filter_by(workflow_id=id).first()
    
    def get_by_name(self, name: str):
        return self.db.query(self.model).filter_by(workflow_name=name).first()
    
    def get_or_create(self, obj: Workflow):
        if type(obj) != Workflow:
            raise ValueError("The argument must be a Workflow object")
        obj_dict = obj.__dict__.copy()
        return super().get_or_create(obj_dict)
