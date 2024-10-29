from . import aws_log_retriever as alr, aws_log_interpreter as ali
from denethor.database.models.Provider import Provider
from denethor.database.models.ProviderConfiguration import ProviderConfiguration
from denethor.database.models.Workflow import Workflow
from denethor.database.models.WorkflowActivity import WorkflowActivity
from denethor.database.models.File import File
from denethor.database.models.ExecutionFile import ExecutionFile
from denethor.database.models.Statistics import Statistics
from denethor.database.models.ExecutionStatistics import ExecutionStatistics
from denethor.database.models.ServiceExecution import ServiceExecution

from denethor.database.repository.ProviderRepository import ProviderRepository
from denethor.database.repository.ProviderConfigurationRepository import ProviderConfigurationRepository
from denethor.database.repository.WorkflowRepository import WorkflowRepository
from denethor.database.repository.WorkflowActivityRepository import WorkflowActivityRepository
from denethor.database.repository.FileRepository import FileRepository
from denethor.database.repository.ExecutionFileRepository import ExecutionFileRepository
from denethor.database.repository.StatisticsRepository import StatisticsRepository
from denethor.database.repository.ExecutionStatisticsRepository import ExecutionStatisticsRepository
from denethor.database.repository.ServiceExecutionRepository import ServiceExecutionRepository


from denethor.database import conn

# Instânciando a sessão do banco de dados
session = conn.Connection().get_session()


# Instânciando as classes de repositórios
provider_repo = ProviderRepository(session)
provider_configuration_repo = ProviderConfigurationRepository(session)
workflow_repo = WorkflowRepository(session)
workflow_activity_repo = WorkflowActivityRepository(session)
file_repo = FileRepository(session)
execution_file_repo = ExecutionFileRepository(session)
statistics_repo = StatisticsRepository(session)
execution_statistics_repo = ExecutionStatisticsRepository(session)
service_execution_repo = ServiceExecutionRepository(session)

# params = {
#     'execution_id': execution_id,
#     'start_time_ms': start_time_ms,
#     'end_time_ms': end_time_ms,
#     'activity': activity,
#     'execution_env': execution_env,
#     'providers': provider,
#     'workflow': workflow,
#     'statistics': statistics
# }
def import_provenance_from_aws(params):
    
    print('Importing provenance from AWS')
    print('params=', params)

    save_workflow_basic_info(params)

    alr.retrieve_logs_from_aws(params)

    ali.process_and_save_logs(params)

    print('Finished importing provenance from AWS')




def save_workflow_basic_info(params):
    # Workflow and provider configuration parameters from the JSON file
    providers = params['providers']
    workflow_dict = params['workflow']
    statistics_dict = params['statistics']
    
    # Service Provider: iterating over the list of service providers and inserting into the database, if not already present
    for provider in providers:
        provider_model = Provider.create_from_dict(provider)
        provider_db, provider_created = provider_repo.get_or_create(provider_model)
        print(f'{"Saving" if provider_created else "Retrieving"} Provider: {provider_db}')

        # Provider Configuration: iterating over the list of configurations and inserting into the database, if not already present
        for config in provider['configurations']:
            config_model = ProviderConfiguration.create_from_dict(config)
            config_model.provider = provider_db
            config_db, config_created = provider_configuration_repo.get_or_create(config_model)
            print(f'{"Saving" if config_created else "Retrieving"} Configuration: {config_db}')

    # Workflow: inserting the workflow information into the database, if not already present
    workflow_model = Workflow.create_from_dict(workflow_dict)
    workflow_db, workflow_created = workflow_repo.get_or_create(workflow_model)
    print(f'{"Saving" if workflow_created else "Retrieving"} Workflow: {workflow_db}')

    # Workflow Activity: iterating over the list of activities and inserting into the database, if not already present
    for activity in workflow_dict['activities']:
        activity_model = WorkflowActivity.create_from_dict(activity)
        activity_model.workflow = workflow_db
        activity_db, activity_created = workflow_activity_repo.get_or_create(activity_model)
        print(f'{"Saving" if activity_created else "Retrieving"} Activity: {activity_db}')


    # Custom Statistics: iterating over the list of custom statistics and inserting into the database, if not already present
    custom_statistics = statistics_dict['custom_statistics']
    for activity_name in custom_statistics:
        for stat in custom_statistics[activity_name]:
            if stat['fieldName'] == 'request_id':
                continue
            stat_model = Statistics(statistics_name=stat['fieldName'], statistics_description=stat['description'])
            stat_db, stat_created = statistics_repo.get_or_create(stat_model)
            print(f'{"Saving" if stat_created else "Retrieving"} Statistics: {stat_db} for Activity: {activity_name}')
