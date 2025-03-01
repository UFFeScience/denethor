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
        info: str,
    ) -> WorkflowExecution:

        files_list = [item["data"] for item in runtime_data.get("input_files")]
        files_csv = ", ".join(files_list)

        files_count = len(files_list) if files_list else 0
        
        duration = end_time_ms - start_time_ms

        workflow_execution_model = WorkflowExecution(
            workflow=workflow,
            execution_tag=execution_tag,
            start_time=du.convert_ms_to_datetime(start_time_ms),
            end_time=du.convert_ms_to_datetime(end_time_ms),
            duration=duration,
            input_count=files_count,
            input_list=files_csv,
            runtime_data="",
            info=info,
        )
        workflow_exec_db = self.workflow_execution_repo.get_or_create(
            workflow_execution_model
        )
        print(f"Saving Workflow Execution: {workflow_exec_db}")

        return workflow_exec_db
