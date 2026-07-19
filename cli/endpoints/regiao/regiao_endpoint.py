import requests
from typing import List, Optional
from .regiao_model import Regiao

class RegiaoEndpoint:

    BASE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/regioes/"

    def buscar_todos(self, order_by: str = "nome") -> List[Regiao]:
        params = {}
        params['orderBy'] = order_by

        resposta = requests.get(self.BASE_URL, params=params)
        resposta.raise_for_status()

        dados = resposta.json()
        lista_regioes = []

        for item in dados:
            regiao = Regiao(
                    id = item.get("id"),
                    nome= item.get("nome"),
                    sigla= item.get("sigla")
                    )

            lista_regioes.append(regiao)

        return lista_regioes

