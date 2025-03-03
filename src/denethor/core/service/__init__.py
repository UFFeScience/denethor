from denethor.core.repository import *

from .WorkflowExecutionService import WorkflowExecutionService
from .StatisticsService import StatisticsService
from .ProviderService import ProviderService
from .WorkflowService import WorkflowService
from .ProviderConfigurationService import ProviderConfigurationService
from .WorkflowActivityService import WorkflowActivityService

from denethor.core.database import session

# Initialize services
workflow_execution_service = WorkflowExecutionService(workflow_execution_repo)
statistics_service = StatisticsService(statistics_repo)
provider_service = ProviderService(provider_repo, provider_conf_repo)
workflow_service = WorkflowService(workflow_repo, workflow_activity_repo)
provider_conf_service = ProviderConfigurationService(provider_conf_repo)
workflow_activity_service = WorkflowActivityService(workflow_activity_repo)
