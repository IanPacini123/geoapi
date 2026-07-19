from fastapi import APIRouter, Depends, HTTPException, Request
from core.limitador import limiter
from core.configuracoes import settings
from sqlalchemy.orm import Session
from core.banco_dados import obter_bd
from core.cache import cache_service
from core.models.ibge_models import Uf, Regiao

router = APIRouter(prefix="/api/localidades/ufs", tags=["Estados (UF)"])

@router.get("")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def listar_ufs(request: Request, db: Session = Depends(obter_bd)):
    chave_cache = "ufs:v1:todos"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    ufs = db.query(Uf).all()
    dados = [{"id": uf.id, "codigo_ibge": uf.codigo_ibge, "sigla": uf.sigla, "nome": uf.nome, "regiao_id": uf.regiao_id} for uf in ufs]
    await cache_service.set(chave_cache, dados)
    return dados

@router.get("/codigo/{codigo_ibge}")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def buscar_uf_por_codigo(request: Request, codigo_ibge: int, db: Session = Depends(obter_bd)):
    chave_cache = f"ufs:v1:codigo:{codigo_ibge}"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    uf = db.query(Uf).filter(Uf.codigo_ibge == codigo_ibge).first()
    if not uf:
        raise HTTPException(status_code=404, detail="Estado (UF) nao encontrado")
        
    dados = {"id": uf.id, "codigo_ibge": uf.codigo_ibge, "sigla": uf.sigla, "nome": uf.nome, "regiao_id": uf.regiao_id}
    await cache_service.set(chave_cache, dados)
    return dados

@router.get("/nome/{nome}")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def buscar_uf_por_nome(request: Request, nome: str, db: Session = Depends(obter_bd)):
    chave_cache = f"ufs:v1:nome:{nome.lower()}"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    ufs = db.query(Uf).filter(Uf.nome.ilike(f"%{nome}%")).all()
    dados = [{"id": uf.id, "codigo_ibge": uf.codigo_ibge, "sigla": uf.sigla, "nome": uf.nome, "regiao_id": uf.regiao_id} for uf in ufs]
    await cache_service.set(chave_cache, dados)
    return dados

@router.get("/regiao/{regiao_sigla}")
@limiter.limit(settings.RATE_LIMIT_GLOBAL)
async def listar_ufs_por_regiao(request: Request, regiao_sigla: str, db: Session = Depends(obter_bd)):
    chave_cache = f"ufs:v1:regiao:{regiao_sigla.upper()}"
    cached = await cache_service.get(chave_cache)
    if cached:
        return cached

    regiao = db.query(Regiao).filter(Regiao.sigla == regiao_sigla.upper()).first()
    if not regiao:
        raise HTTPException(status_code=404, detail="Regiao nao encontrada")
    
    ufs = db.query(Uf).filter(Uf.regiao_id == regiao.id).all()
    dados = [{"id": uf.id, "codigo_ibge": uf.codigo_ibge, "sigla": uf.sigla, "nome": uf.nome, "regiao_id": uf.regiao_id} for uf in ufs]
    await cache_service.set(chave_cache, dados)
    return dados
