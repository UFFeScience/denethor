from denethor.core.model import Provider, ProviderConfiguration
from denethor.core.repository import ProviderRepository, ProviderConfigurationRepository

class ProviderService:
    def __init__(self, provider_repo: ProviderRepository, provider_conf_repo: ProviderConfigurationRepository):
        self.provider_repo = provider_repo
        self.provider_conf_repo = provider_conf_repo


    def get_or_create(self, providers_dict: dict) -> list[Provider]:
        providers: list[Provider] = []

        for prov in providers_dict:
            provider_model = Provider(
                provider_name=prov["provider_name"],
                provider_tag=prov["provider_tag"],
            )

            provider_db, created = self.provider_repo.get_or_create(provider_model)
            print(f'{"Saving" if created else "Retrieving"} Provider: {provider_db}')

            for conf in prov["configurations"]:
                provider_conf_model = ProviderConfiguration(
                    provider=provider_db,
                    timeout=conf["timeout"],
                    cpu=conf["cpu"],
                    memory_mb=conf["memory_mb"],
                    storage_mb=conf["storage_mb"],
                )
                provider_conf_db, created_conf = self.provider_conf_repo.get_or_create(
                    provider_conf_model
                )

                print(
                    f'{"Saving" if created_conf else "Retrieving"} Provider Configuration: {provider_conf_db}'
                )

                provider_db.configurations.append(provider_conf_db)

            providers.append(provider_db)

        return providers
