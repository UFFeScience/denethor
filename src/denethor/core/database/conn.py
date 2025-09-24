import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Parâmetros de conexão a partir das variáveis de ambiente
HOST = os.getenv('DENETHOR_DB_HOST')
PORT = os.getenv('DENETHOR_DB_PORT')
DATABASE = os.getenv('DENETHOR_DB_DATABASE')
USER = os.getenv('DENETHOR_DB_USER')
PASSWORD = os.getenv('DENETHOR_DB_PASSWORD')

class Connection:
    def __init__(self):
        self.db_url = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'
        self.engine = create_engine(self.db_url, connect_args={"connect_timeout": 5})  # Timeout de 5 segundos
        self.Session = sessionmaker(bind=self.engine)

    def simple_test(self):
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except OperationalError:
            return False

    def detailed_test(self):
        try:
            with self.engine.connect() as connection:
                # Obtenha a data e hora atual do banco de dados
                result = connection.execute(text("SELECT NOW()"))
                current_datetime = result.fetchone()[0]

                # Obtenha o SGBD e a versão
                result = connection.execute(text("SELECT version()"))
                db_version = result.fetchone()[0]

            return {
                "status": "success",
                "current_datetime": current_datetime,
                "db_version": db_version
            }
        except OperationalError as e:
            return {
                 "status": "failure",
                "error": str(e)
            }

    def get_session(self):
        connection_info = self.detailed_test()
        if connection_info["status"] == "success":
            print(f"Connected to database. Current datetime: {connection_info['current_datetime']}, DB Version: {connection_info['db_version']}")
            return self.Session()
        else:
            raise ConnectionError(f"Não foi possível conectar ao banco de dados: {connection_info['error']}")