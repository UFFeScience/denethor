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

from .. import conn

# Instânciando a sessão do banco de dados
db = conn.Connection().get_session()


# Instânciando as classes de repositórios
provider_repo = ProviderRepository(db)
provider_conf_repo = ProviderConfigurationRepository(db)
workflow_repo = WorkflowRepository(db)
workflow_activity_repo = WorkflowActivityRepository(db)
workflow_execution_repo = WorkflowExecutionRepository(db)
file_repo = FileRepository(db)
execution_file_repo = ExecutionFileRepository(db)
statistics_repo = StatisticsRepository(db)
execution_statistics_repo = ExecutionStatisticsRepository(db)
service_execution_repo = ServiceExecutionRepository(db)
