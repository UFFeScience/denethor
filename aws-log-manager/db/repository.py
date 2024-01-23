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
        super().__init__(session, WorkflowActivity)

class ServiceExecutionRepository(GenericRepository):
    def __init__(self, session: Session):
        super().__init__(session, ServiceExecution)

class FileRepository(GenericRepository):
    def __init__(self, session: Session):
        super().__init__(session=session, model=File)
    
class ExecutionFilesRepository(GenericRepository):
    def __init__(self, session: Session):
        super().__init__(session, ExecutionFiles)

class StatisticsRepository(GenericRepository):
    def __init__(self, session: Session):
        super().__init__(session, Statistics)

class ExecutionStatisticsRepository(GenericRepository):
    def __init__(self, session: Session):
        super().__init__(session, ExecutionStatistics)

