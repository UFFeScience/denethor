from sqlalchemy.orm import Session
from denethor.database.repository.BaseRepository import BaseRepository
from denethor.database.models.ProviderConfiguration import ProviderConfiguration

class ProviderConfigurationRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session=session, model=ProviderConfiguration)
    
    def get_by_id(self, id: int):
        return self.db.query(self.model).filter_by(configuration_id=id).first()

    def get_by_provider_id(self, provider_id: int):
        return self.db.query(self.model).filter_by(provider_id=provider_id).all()
    
    def get_or_create(self, obj: ProviderConfiguration):
        if type(obj) != ProviderConfiguration:
            raise ValueError("The argument must be a ProviderConfiguration object")
        obj_dict = obj.__dict__.copy()
        return super().get_or_create(obj_dict)