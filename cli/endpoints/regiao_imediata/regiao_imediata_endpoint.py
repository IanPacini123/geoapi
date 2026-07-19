
import requests
from typing import List
from .regiao_imediata_model import RegiaoImediata
from ..regiao_intermediaria.regiao_intermediaria_model import RegiaoIntermediaria

class RegiaoImediataEndpoint:

    BASE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/regioes-imediatas"

    def buscar_todos(self, order_by: str = "nome") -> List[RegiaoImediata]:
        params = {}
        params['orderBy'] = order_by

        resposta = requests.get(self.BASE_URL, params=params)
        resposta.raise_for_status()

        dados = resposta.json()
        lista_regioes_imediatas = []

        for item in dados:
            regiao_intermediaria_dados = item.get("regiao-intermediaria") or {}
            regiao_intermediaria = RegiaoIntermediaria(
                id = regiao_intermediaria_dados.get("id")
            )

            regiao_imediata = RegiaoImediata(
                id = item.get("id"),
                nome = item.get("nome"),
                regiao_intermediaria = regiao_intermediaria 
            )

            lista_regioes_imediatas.append(regiao_imediata)

        return lista_regioes_imediatas

