import requests
from typing import List
from .regiao_intermediaria_model import RegiaoIntermediaria
from ..uf.uf_model import UF

class RegiaoIntermediariaEndpoint:

    BASE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/regioes-intermediarias"

    def buscar_todos(self, order_by: str = "nome") -> List[RegiaoIntermediaria]:
        params = {}
        params['orderBy'] = order_by

        resposta = requests.get(self.BASE_URL, params=params)
        resposta.raise_for_status()

        dados = resposta.json()
        lista_regioes_intermediarias = []

        for item in dados:
            uf_dados = item.get("UF") or {}
            uf = UF(
                id = uf_dados.get("id")
            )

            regiao_intermediaria = RegiaoIntermediaria(
                    id = item.get("id"),
                    nome= item.get("nome"),
                    uf = uf 
            )

            lista_regioes_intermediarias.append(regiao_intermediaria)

        return lista_regioes_intermediarias

