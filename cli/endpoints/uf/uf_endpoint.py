import requests
from typing import List, Optional
from .uf_model import UF
from ..regiao.regiao_model import Regiao

class UFEndpoint:
    
    BASE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"

    def buscar_todos(self, order_by: str = "nome", view: Optional[str] = None) -> List[UF]:
        params = {}
        if order_by:
            params['orderBy'] = order_by
        if view:
            params['view'] = view

        resposta = requests.get(self.BASE_URL, params=params)
        resposta.raise_for_status()
        
        dados = resposta.json()
        lista_ufs = []
        
        for item in dados:
            if view == "nivelado":
                # O formato da resposta muda bastante quando view="nivelado"
                # Neste exemplo, estamos focando no parse padrao (view=None)
                # Para tratar o nivelado, adaptariamos a extracao de chaves.
                pass 
            else:
                regiao_dados = item.get("regiao") or {}
                regiao = Regiao(
                    id=regiao_dados.get("id"),
                    nome=regiao_dados.get("nome"),
                    sigla=regiao_dados.get("sigla")
                )
                
                uf = UF(
                    id=item.get("id"),
                    nome=item.get("nome"),
                    sigla=item.get("sigla"),
                    regiao=regiao
                )
                lista_ufs.append(uf)
                
        return lista_ufs
