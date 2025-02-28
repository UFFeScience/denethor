from denethor.database.model.BaseModel import *

class Task(Base):
    __tablename__ = 'task'
    
    task_id = Column(Integer, primary_key=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey('workflow_activity.activity_id'), nullable=False)
    task_type = Column(Integer, nullable=False)
    input_count = Column(Integer, nullable=False)
    input_list = Column(Text, nullable=False)
    output_count = Column(Integer, nullable=False)
    output_list = Column(Text, nullable=False)

    # Define relationships if needed
    # activity = relationship("WorkflowActivity", back_populates="tasks")
