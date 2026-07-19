from fastapi import APIRouter, Depends, HTTPException, Request
from core.limitador import limiter
from core.configuracoes import settings
from sqlalchemy.orm import Session
from core.banco_dados import obter_bd
from core.cache import cache_service
from core.models.ibge_models import Uf, Regiao, Mesorregiao, Microrregiao, Municipio

router = APIRouter(prefix="/api/localidades/municipios", tags=["Municipios"])

@router.get("")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def listar_todos_municipios(
    request: Request, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(obter_bd)
):
    chave_cache = f"municipios:v1:todos:skip:{skip}:limit:{limit}"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    municipios = db.query(Municipio).offset(skip).limit(limit).all()
    dados = [{"id": m.id, "codigo_ibge": m.codigo_ibge, "nome": m.nome} for m in municipios]
    await cache_service.set(chave_cache, dados)
    return dados

@router.get("/codigo/{codigo_ibge}")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def buscar_municipio_por_codigo(request: Request, codigo_ibge: int, db: Session = Depends(obter_bd)):
    chave_cache = f"municipios:v1:codigo:{codigo_ibge}"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    m = db.query(Municipio).filter(Municipio.codigo_ibge == codigo_ibge).first()
    if not m:
        raise HTTPException(status_code=404, detail="Municipio nao encontrado")
    
    dados = {"id": m.id, "codigo_ibge": m.codigo_ibge, "nome": m.nome}
    await cache_service.set(chave_cache, dados)
    return dados

@router.get("/nome/{nome}")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def buscar_municipios_por_nome(request: Request, nome: str, db: Session = Depends(obter_bd)):
    chave_cache = f"municipios:v1:nome:{nome.lower()}"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    municipios = db.query(Municipio).filter(Municipio.nome.ilike(f"%{nome}%")).all()
    dados = [{"id": m.id, "codigo_ibge": m.codigo_ibge, "nome": m.nome} for m in municipios]
    await cache_service.set(chave_cache, dados)
    return dados

@router.get("/{uf_sigla}")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def listar_municipios_por_uf(request: Request, uf_sigla: str, db: Session = Depends(obter_bd)):
    chave_cache = f"municipios:v1:uf:{uf_sigla.upper()}"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    uf = db.query(Uf).filter(Uf.sigla == uf_sigla.upper()).first()
    if not uf:
        raise HTTPException(status_code=404, detail="UF nao encontrada")

    municipios = db.query(Municipio).join(Microrregiao).join(Mesorregiao).filter(Mesorregiao.uf_id == uf.id).all()
    dados = [{"id": m.id, "codigo_ibge": m.codigo_ibge, "nome": m.nome} for m in municipios]
    await cache_service.set(chave_cache, dados)
    return dados

@router.get("/regiao/{regiao_sigla}")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def listar_municipios_por_regiao(request: Request, regiao_sigla: str, db: Session = Depends(obter_bd)):
    chave_cache = f"municipios:v1:regiao:{regiao_sigla.upper()}"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    regiao = db.query(Regiao).filter(Regiao.sigla == regiao_sigla.upper()).first()
    if not regiao:
        raise HTTPException(status_code=404, detail="Regiao nao encontrada")
        
    municipios = db.query(Municipio).join(Microrregiao).join(Mesorregiao).join(Uf).filter(Uf.regiao_id == regiao.id).all()
    dados = [{"id": m.id, "codigo_ibge": m.codigo_ibge, "nome": m.nome} for m in municipios]
    await cache_service.set(chave_cache, dados)
    return dados
