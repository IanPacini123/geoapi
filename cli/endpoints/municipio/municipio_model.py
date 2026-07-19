from dataclasses import dataclass
from typing import Optional
from ..microrregiao.microrregiao_model import Microrregiao
from ..regiao_imediata.regiao_imediata_model import RegiaoImediata

@dataclass
class Municipio:
    id: int
    nome: str
    microrregiao: Microrregiao
    regiao_imediata: RegiaoImediata
