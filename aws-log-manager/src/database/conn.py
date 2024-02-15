from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Parâmetros de conexão
HOST = 'mribeiro-pg-database.ca8aozgznnhf.sa-east-1.rds.amazonaws.com'
PORT = 9855
DATABASE = 'postgres'
USER = 'postgres'
PASSWORD = 'B3yaRB1pDfBvbUQMkXky'

class Connection:
    def __init__(self):
        self.db_url = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'
        self.engine = create_engine(self.db_url)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()