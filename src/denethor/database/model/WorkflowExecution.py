from denethor.database.model.BaseModel import *

class WorkflowExecution(BaseModel):
    __tablename__ = "workflow_execution"

    we_id = Column(Integer, primary_key=True)
    we_tag = Column(String(255))
    workflow_id = Column(Integer, ForeignKey("workflow.workflow_id"))
    input_files_count = Column(Integer)
    output_files_count = Column(Integer)
    start_time = Column(TIMESTAMP(timezone=True))
    end_time = Column(TIMESTAMP(timezone=True))
    duration = Column(Float)
    runtime_data = Column(Text)
    observations = Column(Text)

    workflow = relationship("Workflow")

    def __str__(self):
        return f"[{self.we_id}]={self.we_tag}"
