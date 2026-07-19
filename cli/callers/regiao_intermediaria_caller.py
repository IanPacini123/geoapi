from utils.chamada_base_endpoint import BaseEndpointCall
from endpoints.regiao_intermediaria.regiao_intermediaria_endpoint import RegiaoIntermediariaEndpoint
from utils.exportador import exportar_para_txt

class RegiaoIntermediariaCaller(BaseEndpointCall):
    def formatar(self, regiao_intermediaria) -> str:
        return f"{regiao_intermediaria.id}, {regiao_intermediaria.nome}, {regiao_intermediaria.uf.id}"

    def coletar(self):
        endpoint = RegiaoIntermediariaEndpoint()
        try:
            lista_regioes_intermediarias = endpoint.buscar_todos(order_by="nome")
            
            if lista_regioes_intermediarias:
                print(f"Sucesso! {len(lista_regioes_intermediarias)} regioes intermediarias encontradas.")
                
                caminho_txt = exportar_para_txt(
                    dados=lista_regioes_intermediarias,
                    funcao_formatadora=self.formatar,
                    nome_arquivo="regioes_intermediarias_ibge",
                    header="ID, NOME, ID_UF"
                )
                
                print(f"Arquivo gerado com sucesso em: {caminho_txt}")
            else:
                print("A busca retornou uma lista vazia.")
                
        except Exception as e:
            print(f"Ocorreu um erro durante a execucao do RegiaoIntermediariaCaller: {e}")
