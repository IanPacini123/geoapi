from utils.chamada_base_endpoint import BaseEndpointCall
from endpoints.microrregiao.microrregiao_endpoint import MicrorregiaoEndpoint
from utils.exportador import exportar_para_txt

class MicrorregiaoCaller(BaseEndpointCall):
    def formatar(self, microrregiao) -> str:
        return f"{microrregiao.id}, {microrregiao.nome}, {microrregiao.mesorregiao.id}"

    def coletar(self):
        endpoint = MicrorregiaoEndpoint()
        try:
            lista_microrregioes = endpoint.buscar_todos(order_by="nome")
            
            if lista_microrregioes:
                print(f"Sucesso! {len(lista_microrregioes)} microrregioes encontradas.")
                
                caminho_txt = exportar_para_txt(
                    dados=lista_microrregioes,
                    funcao_formatadora=self.formatar,
                    nome_arquivo="microrregioes_ibge",
                    header="ID, NOME, ID_MESORREGIAO"
                )
                
                print(f"Arquivo gerado com sucesso em: {caminho_txt}")
            else:
                print("A busca retornou uma lista vazia.")
                
        except Exception as e:
            print(f"Ocorreu um erro durante a execucao do MicrorregiaoCaller: {e}")
