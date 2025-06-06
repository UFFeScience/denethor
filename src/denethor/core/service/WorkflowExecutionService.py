import json
from denethor.core.model import Workflow, WorkflowExecution
from denethor.core.repository import WorkflowExecutionRepository
import denethor.utils.utils as du


class WorkflowExecutionService:
    def __init__(self, workflow_execution_repo: WorkflowExecutionRepository):
        self.workflow_execution_repo = workflow_execution_repo


    def create(
        self,
        workflow: Workflow,
        execution_tag: str,
        start_time_ms: int,
        end_time_ms: int,
        runtime_data: dict,
        info: str = None,
    ) -> WorkflowExecution:

        if runtime_data is None or len(runtime_data) == 0:
            files_list = []
        else:
            files_list = [item["data"] for item in runtime_data.get("input_files")]

        workflow_execution = WorkflowExecution(
            workflow=workflow,
            execution_tag=execution_tag,
            start_time=du.convert_ms_to_datetime(start_time_ms),
            end_time=du.convert_ms_to_datetime(end_time_ms),
            duration=(end_time_ms - start_time_ms),
            input_count=len(files_list) if files_list else 0,
            input_list=json.dumps(files_list),
            runtime_data=json.dumps(runtime_data),
            info=info,
        )
        workflow_exec_db, created = self.workflow_execution_repo.get_or_create(
            workflow_execution
        )

        # TODO: rever isso
        # if not created:
        #     raise ValueError(
        #         f"Workflow Execution with tag {execution_tag} already exists in the database."
        #     )
        
        return workflow_exec_db
