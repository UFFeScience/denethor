from denethor.database.models.BaseModel import *

class ProviderConfiguration(BaseModel):
    __tablename__ = 'provider_configuration'

    configuration_id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey('provider.provider_id'))
    timeout = Column(Integer)
    cpu = Column(Integer)
    memory_mb = Column(Integer)
    storage_mb = Column(Integer)

    provider = relationship("Provider")

    def __str__(self):
        return (f"[{self.configuration_id}], {self.memory_mb}MB RAM, "
                f"{self.timeout}s timeout, {self.cpu}vCPU, {self.storage_mb}MB storage")
