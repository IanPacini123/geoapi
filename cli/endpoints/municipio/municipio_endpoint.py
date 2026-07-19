import requests
from typing import List
from .municipio_model import Municipio
from ..microrregiao.microrregiao_model import Microrregiao
from ..regiao_imediata.regiao_imediata_model import RegiaoImediata

class MunicipioEndpoint:

    BASE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"

    def buscar_todos(self, order_by: str = "nome") -> List[Municipio]:
        params = {}
        params['orderBy'] = order_by

        resposta = requests.get(self.BASE_URL, params=params)
        resposta.raise_for_status()

        dados = resposta.json()
        lista_municipios = []

        for item in dados:
            microrregiao_dados = item.get("microrregiao") or {}
            microrregiao = Microrregiao(
                id = microrregiao_dados.get("id")
            )
            
            regiao_imediata_dados = item.get("regiao-imediata") or {}
            regiao_imediata = RegiaoImediata(
                id = regiao_imediata_dados.get("id")
            )
           
            municipio = Municipio(
                id = item.get("id"),
                nome = item.get("nome"),
                microrregiao = microrregiao,
                regiao_imediata = regiao_imediata
            )

            lista_municipios.append(municipio)

        return lista_municipios

