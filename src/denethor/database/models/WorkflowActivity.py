from denethor.database.models.BaseModel import *

class WorkflowActivity(BaseModel):
    __tablename__ = 'workflow_activity'

    activity_id = Column(Integer, primary_key=True)
    activity_name = Column(String)
    activity_description = Column(String)
    workflow_id = Column(Integer, ForeignKey('workflow.workflow_id'))

    workflow = relationship('Workflow')
    tasks = relationship("Task", back_populates="activity")

    def __str__(self):
        return (f"[{self.activity_id}]={self.activity_name}")
