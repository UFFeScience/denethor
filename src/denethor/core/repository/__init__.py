from .ProviderRepository import ProviderRepository
from .ProviderConfigurationRepository import ProviderConfigurationRepository
from .WorkflowRepository import WorkflowRepository
from .WorkflowActivityRepository import WorkflowActivityRepository
from .WorkflowExecutionRepository import WorkflowExecutionRepository
from .FileRepository import FileRepository
from .ExecutionFileRepository import ExecutionFileRepository
from .StatisticsRepository import StatisticsRepository
from .ExecutionStatisticsRepository import ExecutionStatisticsRepository
from .ServiceExecutionRepository import ServiceExecutionRepository

from ..database import conn

# Instânciando a sessão do banco de dados
session = conn.Connection().get_session()


# Instânciando as classes de repositórios
provider_repo = ProviderRepository(session)
provider_conf_repo = ProviderConfigurationRepository(session)
workflow_repo = WorkflowRepository(session)
workflow_activity_repo = WorkflowActivityRepository(session)
workflow_execution_repo = WorkflowExecutionRepository(session)
file_repo = FileRepository(session)
execution_file_repo = ExecutionFileRepository(session)
statistics_repo = StatisticsRepository(session)
execution_statistics_repo = ExecutionStatisticsRepository(session)
service_execution_repo = ServiceExecutionRepository(session)
