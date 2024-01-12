from generic_repository import *

class RequestLogRepository(GenericRepository):
    def __init__(self, db: Session):
        super().__init__(db, RequestLogRepository)

    def get_by_name(self, name: str):
        return self.db.query(self.model).filter_by(name=name).first()
