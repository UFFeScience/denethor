from database.db_model import *
from database.repository import *
import aws_log_retriever as retriever
import aws_log_interpreter as interpreter

def import_provenance_from_aws(params):
    print('Importing provenance from AWS')

    # Prepare the database with the service provider and workflow information
    providers = params['providers']
    workflow = params['workflow_info']
    execution_id = params['executionId']
    functions = params['functions']
    log_path = params['logPath']
    log_file = params['logFile']

    "providers": PROVIDERS_INFO['providers'],
    "workflow": WORKFLOW_INFO['workflow']['workflow_info'],
    "executionId": execution_id,
    "workflowStartTimeStr": workflow_start_time_str,
    "workflowStartTimeMs": workflow_start_time_ms,
    "files": input_files,
    "path": WORKFLOW_INFO['workflow']['inputFiles']['path'] 

    # Service Provider: iterating over the list of service providers and inserting into the database, if not already present
    for provider in providers:
        provider_model = ServiceProvider.create_from_dict(provider)
        provider_db, provider_created = service_provider_repo.get_or_create(provider_model)
        print(f'{"Saving" if provider_created else "Retrieving"} Provider: {provider_db}')

    # Workflow: inserting the workflow into the database, if not already present
    workflow_model = Workflow.create_from_dict(workflow)
    workflow_db, workflow_created = workflow_repo.get_or_create(workflow_model)
    print(f'{"Saving" if workflow_created else "Retrieving"} Workflow: {workflow_db}')

    # Workflow Activity: iterating over the list of functions (activities) and inserting into the database, if not already present
    for function_name in functions:

        activity = next((act for act in WORKFLOW_INFO['activities'] if act['name'] == function_name), None)
        if activity is None:
            raise ValueError(f"Activity {function_name} not found in workflow activities json file.")
        activity_model = WorkflowActivity.create_from_dict(activity)
        activity_model.workflow = workflow_db
        activity_db, activity_created = workflow_activity_repo.get_or_create(activity_model)
        print(f'{"Saving" if activity_created else "Retrieving"} Activity: {activity_db}')

        default_statistics = WORKFLOW_INFO['defaultStatistics']
        activity_statistics = activity['customStatistics']
        default_sep = WORKFLOW_INFO['defaultLogMessageSeparator']

        # Custom Statistics: iterando sobre as estatísticas customizadas e adicionando ao banco de dados
        for log_type in activity_statistics:
            for stat in activity_statistics[log_type]:
                if stat['fieldName'] != 'request_id':
                    stat_model = Statistics(name=stat['fieldName'], description=stat['description'])
                    stat_db, stat_created = statistics_repo.get_or_create(stat_model)
                    print(f'{"Saving" if stat_created else "Retrieving"} Statistics: {stat_db}')


    retriever.retrieve_logs_from_aws(params)

    interpreter.analyze_logs(params)