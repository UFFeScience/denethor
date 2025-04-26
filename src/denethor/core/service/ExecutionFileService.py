from sqlalchemy.orm import Session
from sqlalchemy import insert, tuple_
from denethor.core.repository.FileRepository import FileRepository
from denethor.core.repository.ExecutionFileRepository import ExecutionFileRepository
from denethor.core.model.File import File
from denethor.core.model.ExecutionFile import ExecutionFile
from denethor.core.service.FileService import FileService



class ExecutionFileService:
    def __init__(self, session: Session):
        self.file_repository = FileRepository(session)
        self.execution_file_repository = ExecutionFileRepository(session)
        self.session = session

    def process_execution_files_in_batch(
        self, execution_files: list, service_execution_db
    ):
        # Extract files from execution_files
        files = [ef.file for ef in execution_files]

        # Use FileService to handle file persistence
        file_service = FileService(self.session)
        existing_files_map = file_service.process_files_in_batch(files)

        # Update execution_files with database references
        for exec_file in execution_files:
            file_key = (
                exec_file.file.file_name,
                exec_file.file.file_bucket,
                exec_file.file.file_path,
            )
            exec_file.file = existing_files_map.get(file_key, exec_file.file)
            exec_file.service_execution = service_execution_db

        # Insert execution_files in batch
        self.session.execute(
            insert(ExecutionFile).values(
                [
                    {
                        "se_id": exec_file.service_execution.se_id,
                        "file_id": exec_file.file.file_id,
                        "transfer_duration": exec_file.transfer_duration,
                        "transfer_type": exec_file.transfer_type,
                    }
                    for exec_file in execution_files
                ]
            )
        )
        self.session.commit()
