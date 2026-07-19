from fastapi import APIRouter, Depends, HTTPException, Request
from core.limitador import limiter
from core.configuracoes import settings
from sqlalchemy.orm import Session
from core.banco_dados import obter_bd
from core.cache import cache_service
from core.models.ibge_models import Pais

router = APIRouter(prefix="/api/localidades/paises", tags=["Paises"])

@router.get("")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def listar_paises(request: Request, db: Session = Depends(obter_bd)):
    chave_cache = "paises:v1:todos"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    paises = db.query(Pais).all()
    dados = [{"id": p.id, "codigo_ibge": p.codigo_ibge, "nome": p.nome} for p in paises]
    await cache_service.set(chave_cache, dados)
    return dados

@router.get("/codigo/{codigo_ibge}")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def buscar_pais_por_codigo(request: Request, codigo_ibge: int, db: Session = Depends(obter_bd)):
    chave_cache = f"paises:v1:codigo:{codigo_ibge}"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    pais = db.query(Pais).filter(Pais.codigo_ibge == codigo_ibge).first()
    if not pais:
        raise HTTPException(status_code=404, detail="Pais nao encontrado")
        
    dados = {"id": pais.id, "codigo_ibge": pais.codigo_ibge, "nome": pais.nome}
    await cache_service.set(chave_cache, dados)
    return dados

@router.get("/nome/{nome}")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def buscar_pais_por_nome(request: Request, nome: str, db: Session = Depends(obter_bd)):
    chave_cache = f"paises:v1:nome:{nome.lower()}"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    paises = db.query(Pais).filter(Pais.nome.ilike(f"%{nome}%")).all()
    dados = [{"id": p.id, "codigo_ibge": p.codigo_ibge, "nome": p.nome} for p in paises]
    await cache_service.set(chave_cache, dados)
    return dados
