from fastapi import APIRouter, Depends, Request
from core.limitador import limiter
from core.configuracoes import settings
from sqlalchemy.orm import Session
from core.banco_dados import obter_bd
from core.models.ibge_models import TipoLogradouro

router = APIRouter(prefix="/api/localidades/tipos-logradouro", tags=["Tipos de Logradouro"])

@router.get("")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
def listar_tipos_logradouro(request: Request, db: Session = Depends(obter_bd)):
    tipos = db.query(TipoLogradouro).all()
    return [{"id": t.id, "sigla": t.sigla, "descricao": t.descricao} for t in tipos]

@router.get("/descricao/{descricao}")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
def buscar_tipo_logradouro_por_descricao(request: Request, descricao: str, db: Session = Depends(obter_bd)):
    tipos = db.query(TipoLogradouro).filter(TipoLogradouro.descricao.ilike(f"%{descricao}%")).all()
    return [{"id": t.id, "sigla": t.sigla, "descricao": t.descricao} for t in tipos]
