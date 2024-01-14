from sqlalchemy.orm import Session
from db_model import *

class GenericRepository:
    def __init__(self, db: Session, model: type):
        self.db = db
        self.model = model

    def get_all(self):
        return self.db.query(self.model).all()

    def get_by_id(self, id: int):
        return self.db.query(self.model).filter_by(id=id).first()

    # ex. pessoa_repo.create({'nome': 'João', 'idade': 30})
    def create(self, obj: dict):
        db_obj = self.model(**obj)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, id: int, obj: dict):
        db_obj = self.get_by_id(id)
        for key, value in obj.items():
            setattr(db_obj, key, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: int):
        db_obj = self.get_by_id(id)
        self.db.delete(db_obj)
        self.db.commit()

class FileRepository(GenericRepository):
    def __init__(self, db: Session):
        super().__init__(db, File)

    def get_by_name(self, name: str) -> File:
        return self.db.query(self.model).filter_by(name=name).first()

class ServiceProviderRepository(GenericRepository):
    def __init__(self, db: Session):
        super().__init__(db, ServiceProvider)

    def get_by_name(self, name: str) -> ServiceProvider:
        return self.db.query(self.model).filter_by(name=name).first()

class WorkflowActivityRepository(GenericRepository):
    def __init__(self, db: Session):
        super().__init__(db, WorkflowActivity)

    def get_by_name(self, name: str) -> WorkflowActivity:
        return self.db.query(self.model).filter_by(name=name).first()



