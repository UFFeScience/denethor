from denethor.database.model.BaseModel import *

class Provider(BaseModel):
    __tablename__ = 'provider'

    provider_id = Column(Integer, primary_key=True)
    provider_name = Column(String)
    provider_tag = Column(String)

    # configurations = relationship("ProviderConfiguration", backref="provider")

    def __str__(self):
        return f"[{self.provider_id}] {self.provider_name}"
