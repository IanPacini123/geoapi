from dataclasses import dataclass
from typing import Optional
from ..mesorregiao.mesorregiao_model import Mesorregiao

@dataclass
class Microrregiao:
    id: int
    nome: Optional[str] = None
    mesorregiao: Optional[Mesorregiao] = None
