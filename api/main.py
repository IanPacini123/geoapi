import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.banco_dados import Base, engine
from api.routers import (
    cep_router,
    paises_router,
    regioes_router,
    ufs_router,
    mesorregioes_router,
    microrregioes_router,
    municipios_router,
    regioes_intermediarias_router,
    regioes_imediatas_router,
    tipos_logradouro_router,
    validacao_router
)
from api.middlewares.auditoria_middleware import AuditoriaMiddleware

from core.configuracoes import settings
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

import core.models

from fastapi.security import APIKeyHeader
from fastapi import Depends

system_id_header = APIKeyHeader(name="X-System-ID", auto_error=False, description="Nome do Sistema Autorizado", scheme_name="X-System-ID")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False, description="Chave de Acesso", scheme_name="X-API-Key")

app = FastAPI(
    title="API GeoCEP",
    description="Servico de busca e enriquecimento de CEP usando a arquitetura Cache-aside",
    version="1.0.0",
    dependencies=[Depends(system_id_header), Depends(api_key_header)]
)

from core.limitador import limiter


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


allowed_origins_list = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "X-System-ID"],
)
app.add_middleware(AuditoriaMiddleware)

app.include_router(cep_router.router)
app.include_router(paises_router.router)
app.include_router(regioes_router.router)
app.include_router(ufs_router.router)
app.include_router(mesorregioes_router.router)
app.include_router(microrregioes_router.router)
app.include_router(municipios_router.router)
app.include_router(regioes_intermediarias_router.router)
app.include_router(regioes_imediatas_router.router)
app.include_router(tipos_logradouro_router.router)
app.include_router(validacao_router.router)

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
