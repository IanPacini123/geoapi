import requests
from typing import List, Optional
from .pais_model import Pais, PaisNome, PaisID

class PaisEndpoint:

    BASE_URL = "https://servicodados.ibge.gov.br/api/v1/paises/"

    def buscar_todos(self, order_by: str = "nome") -> List[Pais]:
        params = {}
        params['orderBy'] = order_by

        resposta = requests.get(self.BASE_URL, params=params)
        resposta.raise_for_status()

        dados = resposta.json()
        lista_paises = []

        for item in dados:
            paisID_dados = item.get("id") or {}
            paisID = PaisID(
                id = paisID_dados.get("M49"),
                iso_3166_1_alpha_2 = paisID_dados.get("ISO-3166-1-ALPHA-2"),
                iso_3166_1_alpha_3 = paisID_dados.get("ISO-3166-1-ALPHA-3")
            )

            paisNome_dados = item.get("nome") or {}
            paisNome = PaisNome(
                abreviado = paisNome_dados.get("abreviado")
            )

            pais = Pais(
                id = paisID,
                nome = paisNome
            )

            lista_paises.append(pais)

        return lista_paises
