from denethor.database.model.BaseModel import *

class Workflow(BaseModel):
    __tablename__ = 'workflow'

    workflow_id = Column(Integer, primary_key=True)
    workflow_name = Column(String, nullable=False)
    workflow_description = Column(String)

    activities = relationship('WorkflowActivity')
    
    def __str__(self):
        return (f"[{self.workflow_id}]={self.workflow_name}")
