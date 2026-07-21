import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def override_db_globally(db_session_memory, monkeypatch):
    from core.banco_dados import obter_bd
    app.dependency_overrides[obter_bd] = lambda: db_session_memory
    
    # Redirecionar logs de auditoria para o SQLite para evitar crachar no finally sem Postgres
    import api.middlewares.auditoria_middleware
    monkeypatch.setattr(api.middlewares.auditoria_middleware, "SessionLocal", lambda: db_session_memory)

    # Mockar chamadas reais ao Redis para evitar timeout
    from core.cache import cache_service
    async def get_mock(key): return "hash_valido"
    async def set_mock(key, value, ex=None): pass
    monkeypatch.setattr(cache_service, "get", get_mock)
    monkeypatch.setattr(cache_service, "set", set_mock)
    
    import hashlib
    import hmac
    def comparacao_mock(a, b): return True
    monkeypatch.setattr(hmac, "compare_digest", comparacao_mock)

    yield
    
    app.dependency_overrides.clear()

def test_cep_endpoint_missing_header():
    response = client.get("/api/localidades/cep/01001000")
    assert response.status_code == 401

def test_cep_endpoint_invalid_cep():
    response = client.get(
        "/api/localidades/cep/123",
        headers={"X-System-ID": "test-system", "X-API-Key": "test"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "CEP invalido"
