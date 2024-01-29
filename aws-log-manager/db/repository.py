from typing import Tuple, Any
from sqlalchemy.orm import Session
from .db_model import *

class GenericRepository:
    def __init__(self, session: Session, model: type):
        self.db = session
        self.model = model

    def get_all(self):
        return self.db.query(self.model).all()

    def get_by_id(self, id: int):
        return self.db.query(self.model).filter_by(id=id).first()
    
    def get_by_attributes(self, obj: dict):
        return self.db.query(self.model).filter_by(**obj).first()
    
    def create(self, obj: dict):
        instance = self.model(**obj)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def get_or_create(self, obj: dict) -> Tuple[Any, bool]:
        obj.pop('_sa_instance_state', None)
        instance = self.get_by_attributes(obj)
        if instance:
            return instance, False
        else:
            return self.create(obj), True
    
    def update(self, id: int, obj: dict):
        instance = self.get_by_id(id)
        for key, value in obj.items():
            setattr(instance, key, value)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, id: int):
        instance = self.get_by_id(id)
        self.db.delete(instance)
        self.db.commit()



class ServiceProviderRepository(GenericRepository):
    def __init__(self, session: Session):
        super().__init__(session=session, model=ServiceProvider)


class WorkflowRepository(GenericRepository):
    def __init__(self, session: Session):
        super().__init__(session=session, model=Workflow)


class WorkflowActivityRepository(GenericRepository):
    def __init__(self, session: Session):
        super().__init__(session=session, model=WorkflowActivity)


class ServiceExecutionRepository(GenericRepository):
    def __init__(self, session: Session):
        super().__init__(session=session, model=ServiceExecution)
    
    def get_or_create(self, obj: ServiceExecution):
        if obj.activity:
            obj.activity_id = obj.activity.id
        if obj.service:
            obj.service_id = obj.service.id
        obj_dict = obj.__dict__.copy()
        obj_dict.pop('execution_files', None)
        obj_dict.pop('execution_statistics', None)
        obj_dict.pop('activity', None)
        obj_dict.pop('service', None)
        return super().get_or_create(obj_dict)


class FileRepository(GenericRepository):
    def __init__(self, session: Session):
        super().__init__(session=session, model=File)
    
    def get_or_create(self, obj: File):
        obj_dict = obj.__dict__.copy()
        obj_dict.pop('execution_file', None)
        return super().get_or_create(obj_dict)


class ExecutionFileRepository(GenericRepository):
    def __init__(self, session: Session):
        super().__init__(session=session, model=ExecutionFile)

    def get_or_create(self, obj: ExecutionFile):
        if obj.file:
            obj.file_id = obj.file.id
        if obj.service_execution:  
            obj.service_execution_id = obj.service_execution.id
        obj_dict = obj.__dict__.copy()
        obj_dict.pop('file', None)
        obj_dict.pop('service_execution', None)
        return super().get_or_create(obj_dict)


class StatisticsRepository(GenericRepository):
    def __init__(self, session: Session):
        super().__init__(session=session, model=Statistics)
    
    def get_or_create(self, obj: Statistics):
        obj_dict = obj.__dict__.copy()
        obj_dict.pop('execution_statistics', None)
        return super().get_or_create(obj_dict)

class ExecutionStatisticsRepository(GenericRepository):
    def __init__(self, session: Session):
        super().__init__(session=session, model=ExecutionStatistics)

    def get_or_create(self, obj: ExecutionStatistics):
        if obj.statistics:
            obj.statistics_id = obj.statistics.id
        if obj.service_execution:  
            obj.service_execution_id = obj.service_execution.id
        obj_dict = obj.__dict__.copy()
        obj_dict.pop('statistics', None)
        obj_dict.pop('service_execution', None)
        return super().get_or_create(obj_dict)

