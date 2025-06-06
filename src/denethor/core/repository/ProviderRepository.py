from sqlalchemy.orm import Session
from denethor.core.repository.BaseRepository import BaseRepository
from denethor.core.model.Provider import Provider

class ProviderRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session=session, model=Provider)
    
    def get_by_id(self, id: int):
        return self.session.query(self.model).filter_by(provider_id=id).first()

    def get_by_name(self, name: str):
        return self.session.query(self.model).filter_by(provider_name=name).first()
    
    def get_by_tag(self, tag: str):
        return self.session.query(self.model).filter_by(provider_tag=tag).first()
    
    def get_or_create(self, obj: Provider):
        if type(obj) != Provider:
            raise ValueError("The argument must be a Provider object")
        obj_dict = obj.__dict__.copy()
        return super().get_or_create(obj_dict)
