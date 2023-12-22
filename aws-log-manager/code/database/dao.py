from sqlalchemy.orm import Session
from conection import Conection

conn = Conection('postgresql://user:password@localhost/mydatabase')

class Dao:
    def __init__(self, model):
        self.session = conn.Session()
        self.model = model

    def add(self, obj):
        self.session.add(obj)
        self.session.commit()

    def query(self):
        return self.session.query(self.model)