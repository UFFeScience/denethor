from denethor.database.models.BaseModel import *

class Statistics(BaseModel):
    __tablename__ = 'statistics'

    statistics_id = Column(Integer, primary_key=True)
    statistics_name = Column(String)
    statistics_description = Column(String)
    
    def __str__(self):
        return (f"[{self.statistics_id}]={self.statistics_name}")
