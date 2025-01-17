from sqlalchemy.orm import Session
from denethor.database.repository.BaseRepository import BaseRepository
from denethor.database.model.ServiceExecution import ServiceExecution

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
        if obj.provider:
            obj.provider_id = obj.provider.provider_id
        obj_dict = obj.__dict__.copy()
        obj_dict.pop('execution_files', None)
        obj_dict.pop('execution_statistics', None)
        obj_dict.pop('activity', None)
        obj_dict.pop('provider', None)
        return super().get_or_create(obj_dict)