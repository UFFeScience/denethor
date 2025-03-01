from denethor.core.model.BaseModel import *

class ExecutionStatistics(BaseModel):
    __tablename__ = 'execution_statistics'

    es_id = Column(Integer, primary_key=True)
    se_id = Column(Integer, ForeignKey('service_execution.se_id'), nullable=False)
    statistics_id = Column(Integer, ForeignKey('statistics.statistics_id'), nullable=False)
    value_float = Column(Float)
    value_integer = Column(Integer)
    value_string = Column(String)

    statistics = relationship("Statistics", backref="execution_statistics")
    service_execution = relationship("ServiceExecution")

    def __str__(self):
        if self.value_float is not None:
            return str(self.value_float)
        elif self.value_integer is not None:
            return str(self.value_integer)
        elif self.value_string is not None:
            return str(self.value_string)
        else:
            return ''