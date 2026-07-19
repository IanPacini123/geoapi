from fastapi import APIRouter, Depends, HTTPException, Request
from core.limitador import limiter
from core.configuracoes import settings
from sqlalchemy.orm import Session
from core.banco_dados import obter_bd
from core.cache import cache_service
from core.models.ibge_models import RegiaoIntermediaria

router = APIRouter(prefix="/api/localidades/regioes-intermediarias", tags=["Regioes Intermediarias"])

@router.get("")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def listar_regioes_intermediarias(request: Request, db: Session = Depends(obter_bd)):
    chave_cache = "regioes_intermediarias:v1:todos"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    ri = db.query(RegiaoIntermediaria).all()
    dados = [{"id": r.id, "codigo_ibge": r.codigo_ibge, "nome": r.nome, "uf_id": r.uf_id} for r in ri]
    await cache_service.set(chave_cache, dados)
    return dados

@router.get("/codigo/{codigo_ibge}")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def buscar_regiao_intermediaria_por_codigo(request: Request, codigo_ibge: int, db: Session = Depends(obter_bd)):
    chave_cache = f"regioes_intermediarias:v1:codigo:{codigo_ibge}"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    ri = db.query(RegiaoIntermediaria).filter(RegiaoIntermediaria.codigo_ibge == codigo_ibge).first()
    if not ri:
        raise HTTPException(status_code=404, detail="Regiao Intermediaria nao encontrada")
        
    dados = {"id": ri.id, "codigo_ibge": ri.codigo_ibge, "nome": ri.nome, "uf_id": ri.uf_id}
    await cache_service.set(chave_cache, dados)
    return dados

@router.get("/nome/{nome}")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def buscar_regiao_intermediaria_por_nome(request: Request, nome: str, db: Session = Depends(obter_bd)):
    chave_cache = f"regioes_intermediarias:v1:nome:{nome.lower()}"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    ris = db.query(RegiaoIntermediaria).filter(RegiaoIntermediaria.nome.ilike(f"%{nome}%")).all()
    dados = [{"id": r.id, "codigo_ibge": r.codigo_ibge, "nome": r.nome, "uf_id": r.uf_id} for r in ris]
    await cache_service.set(chave_cache, dados)
    return dados
