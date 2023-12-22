from sqlalchemy.orm import Session
from models import ServiceExecution
from dao import GenericDao

class ServiceExecutionService:
    def __init__(self, session: Session):
        self.dao = GenericDao(session, ServiceExecution)

    def add(self, obj):
        # Adicione aqui as regras de negócio específicas para ServiceExecution
        self.dao.add(obj)

    def query(self):
        return self.dao.query()


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker








from sqlalchemy.orm import Session
from models import ServiceExecution
from dao import ServiceExecutionDao

class ServiceExecutionService:
    def __init__(self):
        self.dao = ServiceExecutionDao()

    def add(self, obj):
        # Adicione aqui as regras de negócio específicas para ServiceExecution
        self.dao.add(obj)

    def query(self):
        return self.dao.query()



