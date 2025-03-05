from denethor.core.model import Workflow, WorkflowActivity
from denethor.core.repository import WorkflowActivityRepository

class WorkflowActivityService:
    def __init__(self, activity_repo: WorkflowActivityRepository):
        self.activity_repo = activity_repo

    def get_by_name_and_workflow(self, activity_name: str, workflow_db: Workflow) -> WorkflowActivity:
        
        if not activity_name:
            raise ValueError("Activity name is required!")
        if not workflow_db:
            raise ValueError("Workflow is required!")
        
        activity_db = self.activity_repo.get_by_name_and_workflow(activity_name, workflow_db)
        if not activity_db:
            raise ValueError(f"Activity {activity_name} for Workflow {workflow_db.workflow_name} not found in Database!")
        return activity_db
