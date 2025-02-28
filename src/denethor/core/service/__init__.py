from denethor.database.repository import *

from .WorkflowExecutionService import WorkflowExecutionService
from .StatisticsService import StatisticsService
from .ProviderService import ProviderService
from .WorkflowService import WorkflowService

from denethor.database import session

# Initialize repositories
# workflow_execution_repo = WorkflowExecutionRepository(session)
# statistics_repo = StatisticsRepository(session)
# provider_repo = ProviderRepository(session)
# provider_conf_repo = ProviderConfigurationRepository(session)
# workflow_repo = WorkflowRepository(session)
# workflow_activity_repo = WorkflowActivityRepository(session)

# Initialize services
workflow_execution_service = WorkflowExecutionService(workflow_execution_repo)
statistics_service = StatisticsService(statistics_repo)
provider_service = ProviderService(provider_repo, provider_conf_repo)
workflow_service = WorkflowService(workflow_repo, workflow_activity_repo)
