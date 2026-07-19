from fastapi.testclient import TestClient
from unittest.mock import patch
from starlette.middleware.cors import CORSMiddleware
from api.main import app

client = TestClient(app)

@patch.object(CORSMiddleware, "is_allowed_origin", return_value=True)
def test_cors_preflight_without_auth(mock_cors):
    """
    Testa se uma requisicao preflight OPTIONS do CORS passa pelo AuditoriaMiddleware
    sem exigir autenticacao (sem os headers X-System-ID e X-API-Key) e retorna
    os cabecalhos corretos do CORS para uma origem permitida.
    """
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "x-system-id, x-api-key"
    }
    
    response = client.options("/api/localidades/ufs", headers=headers)
    
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    
    # A resposta deve permitir os metodos e os cabecalhos solicitados
    assert "access-control-allow-headers" in response.headers
    assert "x-system-id" in response.headers["access-control-allow-headers"].lower()
    assert "x-api-key" in response.headers["access-control-allow-headers"].lower()

import pytest
import asyncio
import httpx
from core.configuracoes import settings

@pytest.mark.asyncio
@patch.object(CORSMiddleware, "is_allowed_origin", return_value=True)
@patch("core.cache.cache_service._get_redis")
async def test_cors_preflight_rate_limit(mock_get_redis, mock_cors):
    """
    Testa se o limite de taxa customizado para preflight OPTIONS bloqueia requisicoes
    apos o limite ser excedido.
    """
    limit_str = settings.RATE_LIMIT_OPTIONS.split("/")[0]
    limit = int(limit_str) if limit_str.isdigit() else 300
    
    # Mocking redis behavior
    class AsyncMockRedis:
        def __init__(self):
            self.count = 0
        async def incr(self, key):
            self.count += 1
            return self.count
        async def expire(self, key, seconds):
            pass
            
    mock_get_redis.return_value = AsyncMockRedis()
    
    # Fast forward: send limit + 5 requests
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as async_client:
        reqs = []
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        }
        for _ in range(limit + 5):
            reqs.append(async_client.options("/api/localidades/ufs", headers=headers))
            
        resps = await asyncio.gather(*reqs)
        
        statuses = [r.status_code for r in resps]
        assert statuses.count(200) >= limit
        assert statuses.count(429) >= 5
