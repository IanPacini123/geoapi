from utils.chamada_base_endpoint import BaseEndpointCall
from endpoints.mesorregiao.mesorregiao_endpoint import MesorregiaoEndpoint
from utils.exportador import exportar_para_txt

class MesorregiaoCaller(BaseEndpointCall):
    def formatar(self, mesorregiao) -> str:
        return f"{mesorregiao.id}, {mesorregiao.nome}, {mesorregiao.uf.id}"

    def coletar(self):
        endpoint = MesorregiaoEndpoint()
        try:
            lista_mesorregioes = endpoint.buscar_todos(order_by="nome")
            
            if lista_mesorregioes:
                print(f"Sucesso! {len(lista_mesorregioes)} mesorregioes encontradas.")
                
                caminho_txt = exportar_para_txt(
                    dados=lista_mesorregioes,
                    funcao_formatadora=self.formatar,
                    nome_arquivo="mesorregioes_ibge",
                    header="ID, NOME, ID_UF"
                )
                
                print(f"Arquivo gerado com sucesso em: {caminho_txt}")
            else:
                print("A busca retornou uma lista vazia.")
                
        except Exception as e:
            print(f"Ocorreu um erro durante a execucao do MesorregiaoCaller: {e}")
