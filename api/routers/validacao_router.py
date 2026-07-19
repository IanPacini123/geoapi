from fastapi import APIRouter, Depends, Request
from core.limitador import limiter
from core.configuracoes import settings
from sqlalchemy.orm import Session
from core.banco_dados import obter_bd
from api.schemas.validacao_schema import BatchValidationRequest, BatchValidationResponse
from core.models.ibge_models import Municipio, Uf, Pais

router = APIRouter(prefix="/api/localidades", tags=["Validacao em Lote"])

@router.post("/validate-batch", response_model=BatchValidationResponse)
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
def validate_batch(request: Request, payload: BatchValidationRequest, db: Session = Depends(obter_bd)):
    mensagens_erro = []
    
    # 1. Validacao de Municipios
    if payload.municipiosIbge:
        municipios_requisitados = set(payload.municipiosIbge)
        
        # Otimizacao: Busca em lote com in_()
        encontrados_objs = db.query(Municipio.codigo_ibge).filter(
            Municipio.codigo_ibge.in_(municipios_requisitados)
        ).all()
        
        # Extrai apenas os codigos numericos (trazidos como tupla)
        municipios_encontrados = {obj[0] for obj in encontrados_objs if obj[0] is not None}
        
        # Usando Set Difference para achar os que faltaram
        municipios_faltantes = municipios_requisitados - municipios_encontrados
        for codigo in sorted(municipios_faltantes):
            mensagens_erro.append(f"Municipio com IBGE {codigo} nao encontrado.")

    # 2. Validacao de UFs
    if payload.ufsIbge:
        ufs_requisitadas = set(payload.ufsIbge)
        
        encontrados_objs = db.query(Uf.codigo_ibge).filter(
            Uf.codigo_ibge.in_(ufs_requisitadas)
        ).all()
        
        ufs_encontradas = {obj[0] for obj in encontrados_objs if obj[0] is not None}
        
        ufs_faltantes = ufs_requisitadas - ufs_encontradas
        for codigo in sorted(ufs_faltantes):
            mensagens_erro.append(f"UF com IBGE {codigo} nao encontrada.")

    # 3. Validacao de Paises
    if payload.paisesIbge:
        paises_requisitados = set(payload.paisesIbge)
        
        encontrados_objs = db.query(Pais.codigo_ibge).filter(
            Pais.codigo_ibge.in_(paises_requisitados)
        ).all()
        
        paises_encontrados = {obj[0] for obj in encontrados_objs if obj[0] is not None}
        
        paises_faltantes = paises_requisitados - paises_encontrados
        for codigo in sorted(paises_faltantes):
            mensagens_erro.append(f"Pais com IBGE {codigo} nao encontrado.")
            
    valido = len(mensagens_erro) == 0
    
    return BatchValidationResponse(
        valido=valido,
        mensagensErro=mensagens_erro
    )
