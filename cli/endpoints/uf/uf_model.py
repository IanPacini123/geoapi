from dataclasses import dataclass
from typing import Optional
from ..regiao.regiao_model import Regiao

@dataclass
class UF:
    id: int
    nome: Optional[str] = None
    sigla: Optional[str] = None
    regiao: Optional[Regiao] = None
