from utils.chamada_base_endpoint import BaseEndpointCall
from endpoints.municipio.municipio_endpoint import MunicipioEndpoint
from utils.exportador import exportar_para_txt

class MunicipioCaller(BaseEndpointCall):
    def formatar(self, municipio) -> str:
        return f"{municipio.id}, {municipio.nome}, {municipio.microrregiao.id}, {municipio.regiao_imediata.id}"

    def coletar(self):
        endpoint = MunicipioEndpoint()
        try:
            lista_municipios = endpoint.buscar_todos(order_by="nome")
            
            if lista_municipios:
                print(f"Sucesso! {len(lista_municipios)} municipios encontrados.")
                
                caminho_txt = exportar_para_txt(
                    dados=lista_municipios,
                    funcao_formatadora=self.formatar,
                    nome_arquivo="municipios_ibge",
                    header="ID, NOME, ID_MICRORREGIAO, ID_REGIAO_IMEDIATA"
                )
                
                print(f"Arquivo gerado com sucesso em: {caminho_txt}")
            else:
                print("A busca retornou uma lista vazia.")
                
        except Exception as e:
            print(f"Ocorreu um erro durante a execucao do MunicipioCaller: {e}")
