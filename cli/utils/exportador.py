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

    Parametros:
        dados (list): A lista de itens a serem exportados.
        funcao_formatadora: Funcao aplicada a cada item para gerar a linha de texto.
        nome_arquivo (str): O nome do arquivo de saida (sem extensao, se ja nao a tiver).
        extensao (str): A extensao do arquivo de saida. Padrao 'csv'.
        header (str): Cabecalho opcional escrito na primeira linha do arquivo.

    Retorna:
        str: O caminho absoluto do arquivo gerado.

    Receives a list of data and generates a .txt file applying
    the funcao_formatadora to each item.

    Args:
        dados (list): The list of items to export.
        funcao_formatadora: Function applied to each item to generate the text line.
        nome_arquivo (str): The output file name (without extension, if not already present).
        extensao (str): The output file extension. Defaults to 'csv'.
        header (str): Optional header written on the first line of the file.

    Returns:
        str: The absolute path of the generated file.
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
