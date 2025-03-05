from sqlalchemy.orm import Session
from denethor.core.repository.BaseRepository import BaseRepository
from denethor.core.model.ServiceExecution import ServiceExecution

class ServiceExecutionRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session=session, model=ServiceExecution)
    
    def get_by_id(self, id: int):
        return self.db.query(self.model).filter_by(se_id=id).first()
    
    def get_or_create(self, obj: ServiceExecution):
        if type(obj) != ServiceExecution:
            raise ValueError("The argument must be a ServiceExecution object")
        if obj.activity:
            obj.activity_id = obj.activity.activity_id
        if obj.provider_conf:
            obj.provider_conf_id = obj.provider_conf.conf_id
        if obj.workflow_execution:
            obj.we_id = obj.workflow_execution.we_id
        obj_dict = obj.__dict__.copy()
        obj_dict.pop('execution_files', None)
        obj_dict.pop('execution_statistics', None)
        obj_dict.pop('activity', None)
        obj_dict.pop('provider_conf', None)
        obj_dict.pop('workflow_execution', None)
        return super().get_or_create(obj_dict)