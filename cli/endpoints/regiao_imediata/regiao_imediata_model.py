from dataclasses import dataclass
from typing import Optional
from ..regiao_intermediaria.regiao_intermediaria_model import RegiaoIntermediaria

@dataclass
class RegiaoImediata:
    id: int
    nome: Optional[str] = None
    regiao_intermediaria: Optional[RegiaoIntermediaria] = None
