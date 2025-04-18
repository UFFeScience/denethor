from sqlalchemy.orm import Session
from denethor.core.repository.FileRepository import FileRepository
from denethor.core.model.File import File

class FileService:
    def __init__(self, session: Session):
        self.file_repository = FileRepository(session)

    def get_or_create(self, file: File):
        # Validate required fields
        if not all([file.file_name, file.file_bucket, file.file_path]):
            raise ValueError("The File object must have 'file_name', 'file_bucket', and 'file_path' attributes")

        # Search for the file by file_name, file_bucket, and file_path
        existing_file = self.file_repository.session.query(File).filter_by(
            file_name=file.file_name, 
            file_bucket=file.file_bucket, 
            file_path=file.file_path
        ).first()
        if existing_file:
            return existing_file, False

        # If not found, create and save the file
        file_db, created = self.file_repository.get_or_create(file)
        return file_db, created
