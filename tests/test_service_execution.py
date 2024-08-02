# from sqlalchemy.orm import Session
# from datetime import datetime, timezone
# import random
# from src.database.db_model import *
# from src.database.repository import *
# from src.database.conn import Connection


# session = Connection().get_session()
# # Create an instance of GenericRepository for the ServiceExecution table
# service_execution_repo = GenericRepository(session, ServiceExecution)

# provider_repo = ProviderRepository(session)

# workflow_activity_repo = WorkflowActivityRepository(session)

# provider = provider_repo.get_by_name(name='AWS Lambda')
# workflow_activity = workflow_activity_repo.get_by_name(name='tree_constructor')

# # Example: Milliseconds representing start and end times
# start_time_ms = int(datetime.now().timestamp() * 1000)
# duration = random.randint(1000, 20000)
# end_time_ms   = int(datetime.now().timestamp() * 1000) + duration

# # Convert milliseconds to seconds
# start_time_seconds = start_time_ms / 1000.0
# end_time_seconds   = end_time_ms / 1000.0

# # Create datetime objects from the timestamps (in UTC)
# start_dt = datetime.fromtimestamp(start_time_seconds, tz=timezone.utc)
# end_dt   = datetime.fromtimestamp(end_time_seconds, tz=timezone.utc)

# # Insert test record
# record = {
#     'start_time': start_dt,
#     'end_time': end_dt,
#     'duration': duration,
#     'error_message': None,
#     'activity_id': workflow_activity.id,
#     'provider_id': provider.id,
#     'consumed_file_id': None,
#     'produced_file_id': None
# }

# # Create the record
# created_record = service_execution_repo.create(record)
# print("Created record:", created_record)

# # Query the record (by ID)
# record_id = created_record.id
# # record_id = 4
# queried_record = service_execution_repo.get_by_id(record_id)
# print(f"Queried record with ", queried_record)

# # Delete the record (by ID)
# service_execution_repo.delete(record_id)
# print(f"Record with ID {record_id} deleted successfully.")
