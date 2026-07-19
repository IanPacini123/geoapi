from fastapi import APIRouter, Depends, HTTPException, Request
from core.limitador import limiter
from core.configuracoes import settings
from sqlalchemy.orm import Session
from core.banco_dados import obter_bd
from core.cache import cache_service
from core.models.ibge_models import Microrregiao

router = APIRouter(prefix="/api/localidades/microrregioes", tags=["Microrregioes"])

@router.get("")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def listar_microrregioes(request: Request, db: Session = Depends(obter_bd)):
    chave_cache = "microrregioes:v1:todos"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    mr = db.query(Microrregiao).all()
    dados = [{"id": m.id, "codigo_ibge": m.codigo_ibge, "nome": m.nome, "mesorregiao_id": m.mesorregiao_id} for m in mr]
    await cache_service.set(chave_cache, dados)
    return dados

@router.get("/codigo/{codigo_ibge}")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def buscar_microrregiao_por_codigo(request: Request, codigo_ibge: int, db: Session = Depends(obter_bd)):
    chave_cache = f"microrregioes:v1:codigo:{codigo_ibge}"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    mr = db.query(Microrregiao).filter(Microrregiao.codigo_ibge == codigo_ibge).first()
    if not mr:
        raise HTTPException(status_code=404, detail="Microrregiao nao encontrada")
        
    dados = {"id": mr.id, "codigo_ibge": mr.codigo_ibge, "nome": mr.nome, "mesorregiao_id": mr.mesorregiao_id}
    await cache_service.set(chave_cache, dados)
    return dados

@router.get("/nome/{nome}")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def buscar_microrregiao_por_nome(request: Request, nome: str, db: Session = Depends(obter_bd)):
    chave_cache = f"microrregioes:v1:nome:{nome.lower()}"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    mrs = db.query(Microrregiao).filter(Microrregiao.nome.ilike(f"%{nome}%")).all()
    dados = [{"id": m.id, "codigo_ibge": m.codigo_ibge, "nome": m.nome, "mesorregiao_id": m.mesorregiao_id} for m in mrs]
    await cache_service.set(chave_cache, dados)
    return dados
