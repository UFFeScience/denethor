from denethor_provenance.database.db_model import *
from denethor_provenance.database.repository import *
from . import aws_log_retriever as alr, aws_log_interpreter as ali

def import_provenance_from_aws(params):
    
    print('Importing provenance from AWS')

    save_workflow_basic_info(params)

    #retriever.retrieve_logs_from_aws(params)

    ali.process_and_save_logs(params)




def save_workflow_basic_info(params):
    # Workflow and provider configuration parameters from the JSON file
    providers = params['providers']
    workflow_dict = params['workflow']
    activities_dict = workflow_dict['activities']
    
    # Service Provider: iterating over the list of service providers and inserting into the database, if not already present
    for provider in providers:
        provider_model = Provider.create_from_dict(provider)
        provider_db, provider_created = provider_repo.get_or_create(provider_model)
        print(f'{"Saving" if provider_created else "Retrieving"} Provider: {provider_db}')

    # Workflow: inserting the workflow information into the database, if not already present
    workflow_model = Workflow.create_from_dict(workflow_dict)
    workflow_db, workflow_created = workflow_repo.get_or_create(workflow_model)
    print(f'{"Saving" if workflow_created else "Retrieving"} Workflow: {workflow_db}')

    # Workflow Activity: iterating over the list of activities and inserting into the database, if not already present
    for activity in activities_dict:

        activity_model = WorkflowActivity.create_from_dict(activity)
        activity_model.workflow = workflow_db
        activity_db, activity_created = workflow_activity_repo.get_or_create(activity_model)
        print(f'{"Saving" if activity_created else "Retrieving"} Activity: {activity_db}')

        activity_custom_statistics = activity['custom_statistics']

        # Custom Statistics: iterando sobre as estatísticas customizadas e adicionando ao banco de dados
        for log_type in activity_custom_statistics:
            for stat in activity_custom_statistics[log_type]:
                if stat['fieldName'] != 'request_id':
                    stat_model = Statistics(statistics_name=stat['fieldName'], statistics_description=stat['description'])
                    stat_db, stat_created = statistics_repo.get_or_create(stat_model)
                    print(f'{"Saving" if stat_created else "Retrieving"} Statistics: {stat_db}')
