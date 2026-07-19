import os

def exportar_para_txt(
        dados: list,
        funcao_formatadora,
        nome_arquivo: str,
        extensao: str = 'csv',
        header: str = '') -> str:
    """
    Recebe uma lista de dados e gera um arquivo .txt aplicando 
    a funcao_formatadora em cada item.
    """
    # Pega o caminho absoluto da pasta raiz (src)
    src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Caminho da pasta exports
    exports_dir = os.path.join(src_dir, "exports")
    os.makedirs(exports_dir, exist_ok=True)
    
    # Ajustando o nome do arquivo para ter a extensao correta
    if not nome_arquivo.endswith(f".{extensao}"):
        nome_arquivo = f"{nome_arquivo}.{extensao}"

    caminho_final = os.path.join(exports_dir, nome_arquivo)
    
    with open(caminho_final, "w", encoding="utf-8") as f:
        # Se um header foi fornecido, escreve ele na primeira linha
        if header:
            f.write(header + "\n")
        
        for item in dados:
            linha_formatada = funcao_formatadora(item)
            f.write(linha_formatada + "\n")
            
    return caminho_final
