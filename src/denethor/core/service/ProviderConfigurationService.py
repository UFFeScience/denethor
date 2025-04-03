from denethor.core.model import Provider, ProviderConfiguration
from denethor.core.repository import ProviderConfigurationRepository

class ProviderConfigurationService:
    def __init__(self, provider_conf_repo: ProviderConfigurationRepository):
        self.provider_conf_repo = provider_conf_repo

    def get_by_provider_and_memory(self, provider: Provider, memory: int) -> ProviderConfiguration:
        
        if not provider:
            raise ValueError("Provider is required!")
        if not memory:
            # raise ValueError("Memory is required!")
            memory = 0
            
        provider_configuration_db = self.provider_conf_repo.get_by_provider_and_memory(provider, memory)
        if not provider_configuration_db:
            raise ValueError(f"Configuration for provider {provider.provider_name} and memory {memory} not found in Database!")
        return provider_configuration_db
