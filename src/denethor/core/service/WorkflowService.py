from denethor.core.model import Workflow, WorkflowActivity
from denethor.core.repository import WorkflowRepository, WorkflowActivityRepository

class WorkflowService:
    def __init__(self, workflow_repo: WorkflowRepository, workflow_activity_repo: WorkflowActivityRepository):
        self.workflow_repo = workflow_repo
        self.workflow_activity_repo = workflow_activity_repo


    def get_or_create(self, workflow_dict: dict) -> Workflow:
        
        workflow_model = Workflow(
            workflow_name=workflow_dict["workflow_name"],
            workflow_description=workflow_dict["workflow_description"],
        )
        workflow_db, created = self.workflow_repo.get_or_create(workflow_model)
        print(f'{"Saving" if created else "Retrieving"} Workflow: {workflow_db}')

        for act in workflow_dict["activities"]:
            activity_model = WorkflowActivity(
                workflow=workflow_db,
                activity_name=act["activity_name"],
                activity_description=act["activity_description"],
            )
            activity_db, created = self.workflow_activity_repo.get_or_create(activity_model)
            print(f'{"Saving" if created else "Retrieving"} Activity: {activity_db}')
            workflow_db.activities.append(activity_db)

        return workflow_db


    def get_by_name(self, workflow_name: str) -> Workflow:

        if not workflow_name:
            raise ValueError("Workflow name is required!")

        workflow_db = self.workflow_repo.get_by_name(workflow_name)
        if not workflow_db:
            raise ValueError(f"Workflow {workflow_name} not found in Database!")
        return workflow_db