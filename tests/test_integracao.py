import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_auth(monkeypatch):
    from core.cache import cache_service
    async def obter_cache_mock(key):
        return "hash_valido"
    monkeypatch.setattr(cache_service, "get", obter_cache_mock)
    
    import hashlib
    import hmac
    comparacao_original = hmac.compare_digest
    def comparacao_mock(a, b):
        return True
    monkeypatch.setattr(hmac, "compare_digest", comparacao_mock)

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
