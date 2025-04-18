from denethor.core.model.BaseModel import *

class Task(Base):
    __tablename__ = 'task'
    
    task_id = Column(Integer, primary_key=True, autoincrement=False)
    activity_id = Column(Integer, ForeignKey('workflow_activity.activity_id'), nullable=False)
    execution_count = Column(Integer, nullable=False)
    task_type = Column(Integer, nullable=False)
    input_count = Column(Integer, nullable=False)
    input_list = Column(Text, nullable=False)
    output_count = Column(Integer, nullable=False)
    output_list = Column(Text, nullable=False)

    # Mark the table as read-only
    __mapper_args__ = {
        'eager_defaults': False  # Mark the table as read-only since it's a view
    }
