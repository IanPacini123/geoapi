import requests
from typing import List
from .microrregiao_model import Microrregiao
from ..mesorregiao.mesorregiao_model import Mesorregiao

class MicrorregiaoEndpoint:

    BASE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/microrregioes"

    def buscar_todos(self, order_by: str = "nome") -> List[Microrregiao]:
        params = {}
        params['orderBy'] = order_by

        resposta = requests.get(self.BASE_URL, params=params)
        resposta.raise_for_status()

        dados = resposta.json()
        lista_microrregioes = []

        for item in dados:
            mesorregiao_dados = item.get("mesorregiao") or {}
            mesorregiao = Mesorregiao(
                id = mesorregiao_dados.get("id")
            )

            microrregiao = Microrregiao(
                    id = item.get("id"),
                    nome = item.get("nome"),
                    mesorregiao = mesorregiao 
            )

            lista_microrregioes.append(microrregiao)

        return lista_microrregioes

