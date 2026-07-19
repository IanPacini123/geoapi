from slowapi import Limiter
from slowapi.util import get_remote_address
from core.configuracoes import settings
from fastapi import Request

def obter_ip_e_sistema_cliente(request: Request) -> str:
    ip = get_remote_address(request)
    sistema = request.headers.get("x-system-id", "desconhecido")
    # Isolamento total obrigatorio (tudo que chega no limiter ja foi validado pelo middleware)
    return f"{ip}:{sistema}"

limiter = Limiter(
    key_func=obter_ip_e_sistema_cliente, 
    default_limits=[settings.RATE_LIMIT_GLOBAL],
    storage_uri=settings.REDIS_URL,
    in_memory_fallback_enabled=True,
    swallow_errors=True
)
