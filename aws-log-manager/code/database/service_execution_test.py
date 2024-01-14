from sqlalchemy.orm import Session
from db_model import *
from repository import GenericRepository, FileRepository, ServiceProviderRepository, WorkflowActivityRepository
from connection import Connection

session = Connection().get_session()
# Create an instance of GenericRepository for the ServiceExecution table
service_execution_repo = GenericRepository(session, ServiceExecution)

service_provider_repo = ServiceProviderRepository(session)

workflow_activity_repo = WorkflowActivityRepository(session)

service_provider = service_provider_repo.get_by_name(name='AWS Lambda')
workflow_activity = workflow_activity_repo.get_by_name(name='tree_constructor')

# Insert test records (replace with actual IDs)
record1 = {
    'start_time': '2024-01-13 10:00:00',
    'end_time': '2024-01-13 10:00:10',
    'duration': 600,
    'error_message': None,
    'activity_id': workflow_activity.id,
    'service_id': service_provider.id,
    'consumed_file_id': None,
    'produced_file_id': None
}

# Create the record
created_record = service_execution_repo.create(record1)
print("Created record:", created_record)

# Query the record (by ID)
record_id = created_record.id
queried_record = service_execution_repo.get_by_id(record_id)
print(f"Queried record with ID {record_id}:", queried_record)

# Delete the record (by ID)
service_execution_repo.delete(record_id)
print(f"Record with ID {record_id} deleted successfully.")
