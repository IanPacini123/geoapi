from dataclasses import dataclass
from typing import Optional

@dataclass
class PaisID:
    id: int
    iso_3166_1_alpha_2: str
    iso_3166_1_alpha_3: str

@dataclass
class PaisNome:
    abreviado: str

@dataclass
class Pais:
    id: PaisID
    nome: PaisNome
