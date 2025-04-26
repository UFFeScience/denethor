from sqlalchemy.orm import Session
from denethor.core.repository.FileRepository import FileRepository
from denethor.core.model.File import File
from sqlalchemy import tuple_, insert


class FileService:
    def __init__(self, session: Session):
        self.file_repository = FileRepository(session)

    def get_or_create(self, file: File):
        # Validate required fields
        if not all([file.file_name, file.file_bucket, file.file_path]):
            raise ValueError(
                "The File object must have 'file_name', 'file_bucket', and 'file_path' attributes"
            )

        # Search for the file by file_name, file_bucket, and file_path
        existing_file = (
            self.file_repository.session.query(File)
            .filter_by(
                file_name=file.file_name,
                file_bucket=file.file_bucket,
                file_path=file.file_path,
            )
            .first()
        )
        if existing_file:
            return existing_file, False

        # If not found, create and save the file
        file_db, created = self.file_repository.get_or_create(file)
        return file_db, created

    
    def process_files_in_batch(self, files: list[File]):
        """
        Handles the batch creation or retrieval of files.

        Args:
            files (list[File]): A list of File objects.

        Returns:
            dict: A mapping of (file_name, file_bucket, file_path) to File objects from the database.
        """
        # Extract unique files using tuples as keys
        unique_files = {
            (file.file_name, file.file_bucket, file.file_path): file for file in files
        }

        # Build a list of tuples for correlated filtering
        file_filters = list(unique_files.keys())

        # Query existing files with correlated filters
        existing_files = (
            self.file_repository.session.query(File)
            .filter(
                tuple_(File.file_name, File.file_bucket, File.file_path).in_(
                    file_filters
                )
            )
            .all()
        )

        # Map existing files by their unique tuple key
        existing_files_map = {
            (file.file_name, file.file_bucket, file.file_path): file
            for file in existing_files
        }

        # Insert new files in batch
        new_files = [
            file for key, file in unique_files.items() if key not in existing_files_map
        ]
        if new_files:
            self.file_repository.session.execute(
                insert(File).values(
                    [
                        {
                            "file_name": file.file_name,
                            "file_bucket": file.file_bucket,
                            "file_path": file.file_path,
                            "file_size": file.file_size,
                            "file_hash_code": file.file_hash_code,
                        }
                        for file in new_files
                    ]
                )
            )
            self.file_repository.session.commit()

            # Query again to include newly inserted files
            new_files_map = {
                (file.file_name, file.file_bucket, file.file_path): file
                for file in self.file_repository.session.query(File)
                .filter(
                    tuple_(File.file_name, File.file_bucket, File.file_path).in_(
                        file_filters
                    )
                )
                .all()
            }
            existing_files_map.update(new_files_map)

        return existing_files_map
