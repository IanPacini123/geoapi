from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from core.banco_dados import Base

class Pais(Base):
    __tablename__ = "pais"

    id = Column(Integer, primary_key=True, index=True)
    codigo_ibge = Column(Integer, unique=True, index=True, nullable=True)
    nome = Column(String(100), nullable=False)

class Regiao(Base):
    __tablename__ = "regiao"

    id = Column(Integer, primary_key=True, index=True)
    codigo_ibge = Column(Integer, unique=True, index=True, nullable=True)
    sigla = Column(String(5), nullable=False)
    nome = Column(String(100), nullable=False)
    
    ufs = relationship("Uf", back_populates="regiao")

class Uf(Base):
    __tablename__ = "uf"

    id = Column(Integer, primary_key=True, index=True)
    codigo_ibge = Column(Integer, unique=True, index=True, nullable=True)
    sigla = Column(String(2), nullable=False, unique=True)
    nome = Column(String(100), nullable=False)
    regiao_id = Column(Integer, ForeignKey("regiao.id"))

    regiao = relationship("Regiao", back_populates="ufs")
    mesorregioes = relationship("Mesorregiao", back_populates="uf")
    regioes_intermediarias = relationship("RegiaoIntermediaria", back_populates="uf")

class Mesorregiao(Base):
    __tablename__ = "mesorregiao"

    id = Column(Integer, primary_key=True, index=True)
    codigo_ibge = Column(Integer, unique=True, index=True, nullable=True)
    nome = Column(String(150), nullable=False)
    uf_id = Column(Integer, ForeignKey("uf.id"))

    uf = relationship("Uf", back_populates="mesorregioes")
    microrregioes = relationship("Microrregiao", back_populates="mesorregiao")

class Microrregiao(Base):
    __tablename__ = "microrregiao"

    id = Column(Integer, primary_key=True, index=True)
    codigo_ibge = Column(Integer, unique=True, index=True, nullable=True)
    nome = Column(String(150), nullable=False)
    mesorregiao_id = Column(Integer, ForeignKey("mesorregiao.id"))

    mesorregiao = relationship("Mesorregiao", back_populates="microrregioes")
    municipios = relationship("Municipio", back_populates="microrregiao")

class RegiaoIntermediaria(Base):
    __tablename__ = "regiao_intermediaria"

    id = Column(Integer, primary_key=True, index=True)
    codigo_ibge = Column(Integer, unique=True, index=True, nullable=True)
    nome = Column(String(150), nullable=False)
    uf_id = Column(Integer, ForeignKey("uf.id"))

    uf = relationship("Uf", back_populates="regioes_intermediarias")
    regioes_imediatas = relationship("RegiaoImediata", back_populates="regiao_intermediaria")

class RegiaoImediata(Base):
    __tablename__ = "regiao_imediata"

    id = Column(Integer, primary_key=True, index=True)
    codigo_ibge = Column(Integer, unique=True, index=True, nullable=True)
    nome = Column(String(150), nullable=False)
    regiao_intermediaria_id = Column(Integer, ForeignKey("regiao_intermediaria.id"))

    regiao_intermediaria = relationship("RegiaoIntermediaria", back_populates="regioes_imediatas")
    municipios = relationship("Municipio", back_populates="regiao_imediata")

class Municipio(Base):
    __tablename__ = "municipio"

    id = Column(Integer, primary_key=True, index=True)
    codigo_ibge = Column(Integer, unique=True, index=True, nullable=True)
    nome = Column(String(200), nullable=False)
    microrregiao_id = Column(Integer, ForeignKey("microrregiao.id"))
    regiao_imediata_id = Column(Integer, ForeignKey("regiao_imediata.id"))

    microrregiao = relationship("Microrregiao", back_populates="municipios")
    regiao_imediata = relationship("RegiaoImediata", back_populates="municipios")

class TipoLogradouro(Base):
    __tablename__ = "tipo_logradouro"

    id = Column(Integer, primary_key=True, index=True)
    sigla = Column(String(10), nullable=True)
    descricao = Column(String(100), nullable=False)
