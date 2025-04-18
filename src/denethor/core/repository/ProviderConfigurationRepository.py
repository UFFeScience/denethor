from sqlalchemy.orm import Session
from denethor.core.model.Provider import Provider
from denethor.core.model.ProviderConfiguration import ProviderConfiguration
from denethor.core.repository.BaseRepository import BaseRepository

class ProviderConfigurationRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session=session, model=ProviderConfiguration)
    
    def get_by_id(self, id: int):
        return self.session.query(self.model).filter_by(configuration_id=id).first()

    def get_by_provider_id(self, provider_id: int):
        return self.session.query(self.model).filter_by(provider_id=provider_id).all()
    
    def get_by_provider_and_memory(self, provider: Provider, memory: int):
        return self.session.query(self.model).filter_by(provider=provider, memory_mb=memory).first()

    def get_or_create(self, obj: ProviderConfiguration):
        if type(obj) != ProviderConfiguration:
            raise ValueError("The argument must be a ProviderConfiguration object")
        obj_dict = obj.__dict__.copy()
        if obj.provider:
            obj.provider_id = obj.provider.provider_id
        obj_dict = obj.__dict__.copy()
        obj_dict.pop('provider', None)
        return super().get_or_create(obj_dict)