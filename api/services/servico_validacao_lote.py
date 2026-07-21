from typing import List, Tuple
from sqlalchemy.orm import Session
from api.schemas.validacao_schema import BatchValidationRequest
from core.models.ibge_models import Municipio, Uf, Pais

class ServicoValidacaoLote:
    """
    Servico responsavel por validar codigos IBGE em lote contra o banco de dados.
    Service responsible for batch validating IBGE codes against the database.
    """
    def __init__(self, db: Session):
        self.db = db

    def validar(self, carga_dados: BatchValidationRequest) -> Tuple[bool, List[str]]:
        """
        Valida multiplos codigos IBGE simultaneamente usando operacoes de conjuntos.

        Parametros:
            carga_dados (BatchValidationRequest): A requisicao contendo os arrays de codigos IBGE.

        Retorna:
            Tuple[bool, List[str]]: Um booleano indicando se todos os codigos sao validos,
                                    e uma lista de mensagens de erro.

        Validates multiple IBGE codes simultaneously using set operations.

        Args:
            carga_dados (BatchValidationRequest): The request containing arrays of IBGE codes.

        Returns:
            Tuple[bool, List[str]]: A boolean indicating if all codes are valid,
                                    and a list of error messages.
        """
        mensagens_erro = []
        
        if carga_dados.municipiosIbge:
            cidades_solicitadas = set(carga_dados.municipiosIbge)
            objetos_encontrados = self.db.query(Municipio.codigo_ibge).filter(
                Municipio.codigo_ibge.in_(cidades_solicitadas)
            ).all()
            
            cidades_encontradas = {obj[0] for obj in objetos_encontrados if obj[0] is not None}
            cidades_faltantes = cidades_solicitadas - cidades_encontradas
            
            for code in sorted(cidades_faltantes):
                mensagens_erro.append(f"Municipio com IBGE {code} nao encontrado.")

        if carga_dados.ufsIbge:
            ufs_solicitadas = set(carga_dados.ufsIbge)
            objetos_encontrados = self.db.query(Uf.codigo_ibge).filter(
                Uf.codigo_ibge.in_(ufs_solicitadas)
            ).all()
            
            ufs_encontradas = {obj[0] for obj in objetos_encontrados if obj[0] is not None}
            ufs_faltantes = ufs_solicitadas - ufs_encontradas
            
            for code in sorted(ufs_faltantes):
                mensagens_erro.append(f"UF com IBGE {code} nao encontrada.")

        if carga_dados.paisesIbge:
            paises_solicitados = set(carga_dados.paisesIbge)
            objetos_encontrados = self.db.query(Pais.codigo_ibge).filter(
                Pais.codigo_ibge.in_(paises_solicitados)
            ).all()
            
            paises_encontrados = {obj[0] for obj in objetos_encontrados if obj[0] is not None}
            paises_faltantes = paises_solicitados - paises_encontrados
            
            for code in sorted(paises_faltantes):
                mensagens_erro.append(f"Pais com IBGE {code} nao encontrado.")
                
        eh_valido = len(mensagens_erro) == 0
        return eh_valido, mensagens_erro
