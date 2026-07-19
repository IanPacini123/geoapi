from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from core.banco_dados import Base

class AuditoriaRequisicao(Base):
    __tablename__ = "tb_auditoria"

    id = Column(Integer, primary_key=True, index=True)
    sistema_usuario = Column(String(100), nullable=True)
    endpoint = Column(String(250), nullable=False)
    metodo = Column(String(10), nullable=False)
    data_hora = Column(DateTime, default=datetime.utcnow, nullable=False)
    status_code = Column(Integer, nullable=False)
