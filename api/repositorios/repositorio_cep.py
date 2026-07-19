from sqlalchemy.orm import Session
from core.models.cep_model import Cep

class RepositorioCep:
    def __init__(self, db: Session):
        self.db = db

    def get_by_cep(self, cep: str) -> Cep | None:
        return self.db.query(Cep).filter(Cep.cep == cep).first()

    def create(self, cep_data: Cep) -> Cep:
        self.db.add(cep_data)
        self.db.commit()
        self.db.refresh(cep_data)
        return cep_data

    def update(self, cep_data: Cep) -> Cep:
        self.db.commit()
        self.db.refresh(cep_data)
        return cep_data
