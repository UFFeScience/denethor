from denethor.core.model.BaseModel import *

class WorkflowExecution(BaseModel):
    __tablename__ = "workflow_execution"

    we_id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey("workflow.workflow_id"), nullable=False)
    execution_tag = Column(String(255), nullable=False)
    start_time = Column(TIMESTAMP(timezone=True), nullable=False)
    end_time = Column(TIMESTAMP(timezone=True), nullable=False)
    duration = Column(Float, nullable=False)
    input_count = Column(Integer, nullable=False)
    input_list = Column(Text)
    runtime_data = Column(Text)
    info = Column(Text)

    workflow = relationship("Workflow")

    def __str__(self):
        return f"[{self.we_id}]={self.execution_tag}"
