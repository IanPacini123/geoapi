from utils.chamada_base_endpoint import BaseEndpointCall
from endpoints.regiao_imediata.regiao_imediata_endpoint import RegiaoImediataEndpoint
from utils.exportador import exportar_para_txt

class RegiaoImediataCaller(BaseEndpointCall):
    def formatar(self, regiao_imediata) -> str:
        return f"{regiao_imediata.id}, {regiao_imediata.nome}, {regiao_imediata.regiao_intermediaria.id}"

    def coletar(self):
        endpoint = RegiaoImediataEndpoint()
        try:
            lista_regioes_imediatas = endpoint.buscar_todos(order_by="nome")
            
            if lista_regioes_imediatas:
                print(f"Sucesso! {len(lista_regioes_imediatas)} regioes imediatas encontradas.")
                
                caminho_txt = exportar_para_txt(
                    dados=lista_regioes_imediatas,
                    funcao_formatadora=self.formatar,
                    nome_arquivo="regioes_imediatas_ibge",
                    header="ID, NOME, ID_REGIAO_INTERMEDIARIA"
                )
                
                print(f"Arquivo gerado com sucesso em: {caminho_txt}")
            else:
                print("A busca retornou uma lista vazia.")
                
        except Exception as e:
            print(f"Ocorreu um erro durante a execucao do RegiaoImediataCaller: {e}")
