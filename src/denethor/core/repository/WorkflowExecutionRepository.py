from typing import Tuple
from sqlalchemy.orm import Session
from denethor.core.repository.BaseRepository import BaseRepository
from denethor.core.model.WorkflowExecution import WorkflowExecution

class WorkflowExecutionRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session=session, model=WorkflowExecution)

    def get_by_id(self, id: int):
        return self.session.query(self.model).filter_by(we_id=id).first()
    
    def get_by_tag(self, tag: str):
        return self.session.query(self.model).filter_by(execution_tag=tag).first()
    
    def get_or_create(self, obj: WorkflowExecution) -> Tuple[WorkflowExecution, bool]:
        if type(obj) != WorkflowExecution:
            raise ValueError("The argument must be a WorkflowExecution object")
        if obj.workflow:
            obj.workflow_id = obj.workflow.workflow_id
        obj_dict = obj.__dict__.copy()
        obj_dict.pop('workflow', None)
        return super().get_or_create(obj_dict)
