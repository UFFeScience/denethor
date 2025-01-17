from sqlalchemy.orm import Session
from denethor.database.repository.BaseRepository import BaseRepository
from denethor.database.model.Workflow import  Workflow
from denethor.database.model.WorkflowActivity import  WorkflowActivity

class WorkflowActivityRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session=session, model=WorkflowActivity)

    def get_by_id(self, id: int):
        return self.db.query(self.model).filter_by(activity_id=id).first()
    
    def get_by_name_and_workflow(self, name: str, workflow: Workflow):
        return self.db.query(self.model).filter_by(activity_name=name, workflow=workflow).first()
    
    def get_or_create(self, obj: WorkflowActivity):
        if type(obj) != WorkflowActivity:
            raise ValueError("The argument must be a WorkflowActivity object")
        if obj.workflow:
            obj.workflow_id = obj.workflow.workflow_id
        obj_dict = obj.__dict__.copy()
        obj_dict.pop('additionalStatistics', None)
        obj_dict.pop('workflow', None)
        return super().get_or_create(obj_dict)