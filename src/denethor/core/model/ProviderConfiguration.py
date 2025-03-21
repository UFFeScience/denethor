from denethor.core.model.BaseModel import *

class ProviderConfiguration(BaseModel):
    __tablename__ = 'provider_configuration'

    conf_id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey('provider.provider_id'), nullable=False)
    timeout = Column(Integer, nullable=False)
    cpu = Column(Integer, nullable=False)
    memory_mb = Column(Integer, nullable=False)
    storage_mb = Column(Integer, nullable=False)

    provider = relationship("Provider")

    def __str__(self):
        return (f"[{self.conf_id}], {self.memory_mb}MB RAM, "
                f"{self.timeout}s timeout, {self.cpu}vCPU, {self.storage_mb}MB storage")
