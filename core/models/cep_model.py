from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from datetime import datetime
from core.banco_dados import Base

class Cep(Base):
    __tablename__ = "tb_cep"

    cep = Column(String(8), primary_key=True, index=True)
    logradouro = Column(String(250), nullable=True)
    bairro = Column(String(150), nullable=True)
    localidade = Column(String(150), nullable=True)
    uf = Column(String(2), nullable=True)
    

    uf_codigo = Column(Integer, ForeignKey("uf.id"), nullable=True)
    municipio_codigo = Column(Integer, ForeignKey("municipio.id"), nullable=True)
    tipo_logradouro_codigo = Column(Integer, ForeignKey("tipo_logradouro.id"), nullable=True)
    
    data_criacao = Column(DateTime, default=datetime.utcnow, nullable=False)

    from sqlalchemy.orm import relationship
    uf_rel = relationship("Uf", foreign_keys=[uf_codigo])
    municipio_rel = relationship("Municipio", foreign_keys=[municipio_codigo])
    tipo_logradouro_rel = relationship("TipoLogradouro", foreign_keys=[tipo_logradouro_codigo])
