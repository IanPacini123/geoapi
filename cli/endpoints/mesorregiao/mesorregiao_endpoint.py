import requests
from typing import List
from .mesorregiao_model import Mesorregiao
from ..uf.uf_model import UF

class MesorregiaoEndpoint:

    BASE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/mesorregioes"

    def buscar_todos(self, order_by: str = "nome") -> List[Mesorregiao]:
        params = {}
        params['orderBy'] = order_by

        resposta = requests.get(self.BASE_URL, params=params)
        resposta.raise_for_status()

        dados = resposta.json()
        lista_mesorregioes = []

        for item in dados:
            uf_dados = item.get("UF") or {}
            uf = UF(
                id = uf_dados.get("id")
            )

            mesorregiao = Mesorregiao(
                    id = item.get("id"),
                    nome= item.get("nome"),
                    uf = uf 
            )

            lista_mesorregioes.append(mesorregiao)

        return lista_mesorregioes

