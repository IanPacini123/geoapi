from utils.chamada_base_endpoint import BaseEndpointCall
from endpoints.uf.uf_endpoint import UFEndpoint
from utils.exportador import exportar_para_txt

class UFCaller(BaseEndpointCall):
    def formatar(self, uf) -> str:
        return f"{uf.id}, {uf.nome}, {uf.sigla}, {uf.regiao.id}"

    def coletar(self):
        endpoint = UFEndpoint()
        try:
            lista_estados = endpoint.buscar_todos(order_by="nome")
            
            if lista_estados:
                print(f"Sucesso! {len(lista_estados)} estados encontrados.")
                
                caminho_txt = exportar_para_txt(
                    dados=lista_estados,
                    funcao_formatadora=self.formatar,
                    nome_arquivo="estados_ibge",
                    header="ID, NOME, SIGLA, ID_REGIAO"
                )
                
                print(f"Arquivo gerado com sucesso em: {caminho_txt}")
            else:
                print("A busca retornou uma lista vazia.")
                
        except Exception as e:
            print(f"Ocorreu um erro durante a execucao do UFCaller: {e}")
