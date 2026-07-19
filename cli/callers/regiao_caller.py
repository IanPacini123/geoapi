from utils.chamada_base_endpoint import BaseEndpointCall
from endpoints.regiao.regiao_endpoint import RegiaoEndpoint
from utils.exportador import exportar_para_txt

class RegiaoCaller(BaseEndpointCall):
    def formatar(self, regiao) -> str:
        return f"{regiao.id}, {regiao.nome}, {regiao.sigla}"

    def coletar(self):
        endpoint = RegiaoEndpoint()
        try:
            lista_regioes = endpoint.buscar_todos(order_by="nome")
            
            if lista_regioes:
                print(f"Sucesso! {len(lista_regioes)} regioes encontradas.")
                
                caminho_txt = exportar_para_txt(
                    dados=lista_regioes,
                    funcao_formatadora=self.formatar,
                    nome_arquivo="regioes_ibge",
                    header="ID, NOME, SIGLA"
                )
                
                print(f"Arquivo gerado com sucesso em: {caminho_txt}")
            else:
                print("A busca retornou uma lista vazia.")
                
        except Exception as e:
            print(f"Ocorreu um erro durante a execucao do RegiaoCaller: {e}")
