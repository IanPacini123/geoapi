from fastapi import APIRouter, Depends, HTTPException, Request
from core.limitador import limiter
from core.configuracoes import settings
from sqlalchemy.orm import Session
from core.banco_dados import obter_bd
from core.cache import cache_service
from core.models.ibge_models import Regiao

router = APIRouter(prefix="/api/localidades/regioes", tags=["Regioes"])

@router.get("")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def listar_regioes(request: Request, db: Session = Depends(obter_bd)):
    chave_cache = "regioes:v1:todos"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    regioes = db.query(Regiao).all()
    dados = [{"id": r.id, "codigo_ibge": r.codigo_ibge, "sigla": r.sigla, "nome": r.nome} for r in regioes]
    await cache_service.set(chave_cache, dados)
    return dados

@router.get("/codigo/{codigo_ibge}")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def buscar_regiao_por_codigo(request: Request, codigo_ibge: int, db: Session = Depends(obter_bd)):
    chave_cache = f"regioes:v1:codigo:{codigo_ibge}"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    regiao = db.query(Regiao).filter(Regiao.codigo_ibge == codigo_ibge).first()
    if not regiao:
        raise HTTPException(status_code=404, detail="Regiao nao encontrada")
        
    dados = {"id": regiao.id, "codigo_ibge": regiao.codigo_ibge, "sigla": regiao.sigla, "nome": regiao.nome}
    await cache_service.set(chave_cache, dados)
    return dados

@router.get("/nome/{nome}")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def buscar_regiao_por_nome(request: Request, nome: str, db: Session = Depends(obter_bd)):
    chave_cache = f"regioes:v1:nome:{nome.lower()}"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    regioes = db.query(Regiao).filter(Regiao.nome.ilike(f"%{nome}%")).all()
    dados = [{"id": r.id, "codigo_ibge": r.codigo_ibge, "sigla": r.sigla, "nome": r.nome} for r in regioes]
    await cache_service.set(chave_cache, dados)
    return dados
