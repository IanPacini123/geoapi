from fastapi import APIRouter, Depends, HTTPException, Request
from core.limitador import limiter
from core.configuracoes import settings
from sqlalchemy.orm import Session
from core.banco_dados import obter_bd
from core.cache import cache_service
from core.models.ibge_models import Mesorregiao

router = APIRouter(prefix="/api/localidades/mesorregioes", tags=["Mesorregioes"])

@router.get("")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def listar_mesorregioes(request: Request, db: Session = Depends(obter_bd)):
    chave_cache = "mesorregioes:v1:todos"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    mr = db.query(Mesorregiao).all()
    dados = [{"id": m.id, "codigo_ibge": m.codigo_ibge, "nome": m.nome, "uf_id": m.uf_id} for m in mr]
    await cache_service.set(chave_cache, dados)
    return dados

@router.get("/codigo/{codigo_ibge}")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def buscar_mesorregiao_por_codigo(request: Request, codigo_ibge: int, db: Session = Depends(obter_bd)):
    chave_cache = f"mesorregioes:v1:codigo:{codigo_ibge}"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    mr = db.query(Mesorregiao).filter(Mesorregiao.codigo_ibge == codigo_ibge).first()
    if not mr:
        raise HTTPException(status_code=404, detail="Mesorregiao nao encontrada")
        
    dados = {"id": mr.id, "codigo_ibge": mr.codigo_ibge, "nome": mr.nome, "uf_id": mr.uf_id}
    await cache_service.set(chave_cache, dados)
    return dados

@router.get("/nome/{nome}")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def buscar_mesorregiao_por_nome(request: Request, nome: str, db: Session = Depends(obter_bd)):
    chave_cache = f"mesorregioes:v1:nome:{nome.lower()}"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    mrs = db.query(Mesorregiao).filter(Mesorregiao.nome.ilike(f"%{nome}%")).all()
    dados = [{"id": m.id, "codigo_ibge": m.codigo_ibge, "nome": m.nome, "uf_id": m.uf_id} for m in mrs]
    await cache_service.set(chave_cache, dados)
    return dados
