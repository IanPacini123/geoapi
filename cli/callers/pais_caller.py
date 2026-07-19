from utils.chamada_base_endpoint import BaseEndpointCall
from endpoints.pais.pais_endpoint import PaisEndpoint
from utils.exportador import exportar_para_txt

class PaisCaller(BaseEndpointCall):
    def formatar(self, pais) -> str:
        return f"{pais.id.id}, {pais.nome.abreviado}, {pais.id.iso_3166_1_alpha_2}, {pais.id.iso_3166_1_alpha_3}"

    def coletar(self):
        endpoint = PaisEndpoint()
        try:
            lista_paises = endpoint.buscar_todos()
            
            if lista_paises:
                print(f"Sucesso! {len(lista_paises)} paises encontrados.")
                
                caminho_txt = exportar_para_txt(
                    dados=lista_paises,
                    funcao_formatadora=self.formatar,
                    nome_arquivo="paises_ibge",
                    header="ID, NOME, ISO2, ISO3"
                )
                
                print(f"Arquivo gerado com sucesso em: {caminho_txt}")
            else:
                print("A busca retornou uma lista vazia.")
                
        except Exception as e:
            print(f"Ocorreu um erro durante a execucao do PaisCaller: {e}")
