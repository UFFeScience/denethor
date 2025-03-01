from typing import Tuple, Any
from sqlalchemy.orm import Session

class BaseRepository:
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