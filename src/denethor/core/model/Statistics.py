from denethor.core.model.BaseModel import *

class Statistics(BaseModel):
    __tablename__ = 'statistics'

    statistics_id = Column(Integer, primary_key=True)
    statistics_name = Column(String, nullable=False)
    statistics_description = Column(String, nullable=False)
    
    def __str__(self):
        return (f"[{self.statistics_id}]={self.statistics_name}")
