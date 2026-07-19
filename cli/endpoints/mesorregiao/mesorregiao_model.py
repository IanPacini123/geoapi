from dataclasses import dataclass
from typing import Optional
from ..uf.uf_model import UF

@dataclass
class Mesorregiao:
    id: int
    nome: Optional[str] = None
    uf: Optional[UF] = None
    
