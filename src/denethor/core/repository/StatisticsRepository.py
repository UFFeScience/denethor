from sqlalchemy.orm import Session
from denethor.core.repository.BaseRepository import BaseRepository
from denethor.core.model.Statistics import Statistics

class StatisticsRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session=session, model=Statistics)
    
    def get_by_id(self, id: int):
        return self.session.query(self.model).filter_by(statistics_id=id).first()
    
    def get_by_name(self, name: str):
        return self.session.query(self.model).filter_by(statistics_name=name).first()
    
    def get_or_create(self, obj: Statistics):
        if type(obj) != Statistics:
            raise ValueError("The argument must be a Statistics object")
        obj_dict = obj.__dict__.copy()
        obj_dict.pop('execution_statistics', None)
        return super().get_or_create(obj_dict)