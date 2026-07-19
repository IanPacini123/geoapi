from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CepResponse(BaseModel):
    cep: str
    logradouro: Optional[str] = None
    bairro: Optional[str] = None
    localidade: Optional[str] = None
    uf: Optional[str] = None
    uf_codigo: Optional[int] = None
    municipio_codigo: Optional[int] = None
    tipo_logradouro_codigo: Optional[int] = None
    data_criacao: Optional[datetime] = None

    class Config:
        from_attributes = True
