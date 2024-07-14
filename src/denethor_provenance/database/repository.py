from typing import Tuple, Any
from sqlalchemy.orm import Session
from src.denethor_provenance.database.db_model import *

class GenericRepository:
    def __init__(self, session: Session, model: type):
        self.db = session
        self.model = model

    def get_all(self):
        return self.db.query(self.model).all()

    def get_by_attributes(self, obj: dict):
        return self.db.query(self.model).filter_by(**obj).first()
    
    def create(self, obj: dict):
        instance = self.model(**obj)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def get_or_create(self, obj: dict) -> Tuple[Any, bool]:
        if type(obj) != dict:
            raise ValueError("The argument must be a dictionary")
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
    
    def get_by_id(self, id: int):
        return self.db.query(self.model).filter_by(provider_id=id).first()

    def get_by_name(self, name: str):
        return self.db.query(self.model).filter_by(provider_name=name).first()
    
    def get_or_create(self, obj: ServiceProvider):
        if type(obj) != ServiceProvider:
            raise ValueError("The argument must be a ServiceProvider object")
        obj_dict = obj.__dict__.copy()
        return super().get_or_create(obj_dict)


class WorkflowRepository(GenericRepository):
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


class WorkflowActivityRepository(GenericRepository):
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


class ServiceExecutionRepository(GenericRepository):
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


class FileRepository(GenericRepository):
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


class ExecutionFileRepository(GenericRepository):
    def __init__(self, session: Session):
        super().__init__(session=session, model=ExecutionFile)

    def get_by_id(self, id: int):
        return self.db.query(self.model).filter_by(ef_id=id).first()
    
    def get_or_create(self, obj: ExecutionFile):
        if type(obj) != ExecutionFile:
            raise ValueError("The argument must be a ExecutionFile object")
        if obj.file:
            obj.file_id = obj.file.file_id
        if obj.service_execution:  
            obj.se_id = obj.service_execution.se_id
        obj_dict = obj.__dict__.copy()
        obj_dict.pop('file', None)
        obj_dict.pop('service_execution', None)
        return super().get_or_create(obj_dict)


class StatisticsRepository(GenericRepository):
    def __init__(self, session: Session):
        super().__init__(session=session, model=Statistics)
    
    def get_by_id(self, id: int):
        return self.db.query(self.model).filter_by(statistics_id=id).first()
    
    def get_by_name(self, name: str):
        return self.db.query(self.model).filter_by(statistics_name=name).first()
    
    def get_or_create(self, obj: Statistics):
        if type(obj) != Statistics:
            raise ValueError("The argument must be a Statistics object")
        obj_dict = obj.__dict__.copy()
        obj_dict.pop('execution_statistics', None)
        return super().get_or_create(obj_dict)


class ExecutionStatisticsRepository(GenericRepository):
    def __init__(self, session: Session):
        super().__init__(session=session, model=ExecutionStatistics)

    def get_by_id(self, id: int):
        return self.db.query(self.model).filter_by(es_id=id).first()
    
    def get_or_create(self, obj: ExecutionStatistics):
        if type(obj) != ExecutionStatistics:
            raise ValueError("The argument must be a ExecutionStatistics object")
        if obj.statistics:
            obj.statistics_id = obj.statistics.statistics_id
        if obj.service_execution:  
            obj.se_id = obj.service_execution.se_id
        obj_dict = obj.__dict__.copy()
        obj_dict.pop('statistics', None)
        obj_dict.pop('service_execution', None)
        return super().get_or_create(obj_dict)




from database.conn import *

# Instânciando a sessão do banco de dados
session = Connection().get_session()

# Instânciando as classes de repositórios
service_provider_repo = ServiceProviderRepository(session)
workflow_repo = WorkflowRepository(session)
workflow_activity_repo = WorkflowActivityRepository(session)
file_repo = FileRepository(session)
execution_file_repo = ExecutionFileRepository(session)
statistics_repo = StatisticsRepository(session)
execution_statistics_repo = ExecutionStatisticsRepository(session)
service_execution_repo = ServiceExecutionRepository(session)