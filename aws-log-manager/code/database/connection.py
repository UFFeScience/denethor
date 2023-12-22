from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Parâmetros de conexão
host = 'mribeiro-pg-database.ca8aozgznnhf.sa-east-1.rds.amazonaws.com'
port = 5432
database = 'postgres'
user = 'postgres'
password = 'postgres'

class Conection:
    def __init__(self):
        self.db_url = 'postgresql://{user}:{password}@{host}/{database}'
        self.engine = create_engine(self.db_url)
        self.Session = sessionmaker(bind=self.engine)