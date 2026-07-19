from sqlalchemy.orm import Session
from core.models.auditoria_model import AuditoriaRequisicao

class RepositorioAuditoria:
    def __init__(self, db: Session):
        self.db = db

    def create(self, auditoria_data: AuditoriaRequisicao) -> AuditoriaRequisicao:
        self.db.add(auditoria_data)
        self.db.commit()
        self.db.refresh(auditoria_data)
        return auditoria_data
