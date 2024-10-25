from denethor.database.repository.BaseRepository import *
from denethor.database.models import ExecutionStatistics

class ExecutionStatisticsRepository(BaseRepository):
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