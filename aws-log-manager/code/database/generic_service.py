from dao import GenericDao

class GenericService:
    def __init__(self, model):
        self.dao = GenericDao(model)

    def add(self, obj):
        self.dao.add(obj)

    def query(self):
        return self.dao.query()
