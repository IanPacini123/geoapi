from sqlalchemy import Column, Integer, String, Boolean, DateTime
from core.banco_dados import Base
from datetime import datetime

class SistemaAutorizado(Base):
    __tablename__ = "sistemas_autorizados"

    id = Column(Integer, primary_key=True, index=True)
    nome_sistema = Column(String(100), unique=True, index=True, nullable=False)
    chave_hash = Column(String(64), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
