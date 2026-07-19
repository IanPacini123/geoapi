import pytest
from fastapi.testclient import TestClient
from api.main import app
from core.configuracoes import settings

client = TestClient(app)

def test_no_headers_blocked():
    """ Sem nenhum cabecalho """
    resp = client.get("/api/localidades/ufs")
    assert resp.status_code == 401
    assert "X-System-ID" in resp.json()["detail"]

def test_missing_x_system_id_blocked():
    """ Apenas X-API-Key sem X-System-ID """
    resp = client.get("/api/localidades/ufs", headers={"X-API-Key": "some_key"})
    assert resp.status_code == 401
    assert "X-System-ID" in resp.json()["detail"]

def test_missing_api_key_blocked():
    """ Apenas X-System-ID sem X-API-Key """
    resp = client.get("/api/localidades/ufs", headers={"X-System-ID": "sys_a_untrusted"})
    assert resp.status_code == 401
    assert "X-API-Key ausente ou invalida" in resp.json()["detail"]

def test_invalid_api_key_blocked(monkeypatch):
    """ Chave invalida para um sistema existente """
    from core.cache import cache_service
    
    async def obter_cache_mock(key):
        if key == "auth:sys_invalid":
            return "hash_valido"
        return None
    monkeypatch.setattr(cache_service, "get", obter_cache_mock)

    resp = client.get("/api/localidades/ufs", headers={"X-System-ID": "sys_invalid", "X-API-Key": "wrong_key"})
    assert resp.status_code == 401
    assert "X-API-Key ausente ou invalida" in resp.json()["detail"]

def test_revoked_api_key_blocked(monkeypatch):
    """ Chave revogada (Nao existe no DB nem no Cache) """
    from core.cache import cache_service
    
    async def obter_cache_mock(key):
        return None # Cache miss
    monkeypatch.setattr(cache_service, "get", obter_cache_mock)

    # Precisamos mockar a consulta no banco de dados para retornar None (sistema revogado/nao existe)
    from core.banco_dados import SessionLocal
    class MockQuery:
        def filter(self, *args, **kwargs): return self
        def first(self): return None
    class MockSession:
        def query(self, *args, **kwargs): return MockQuery()
        def close(self): pass
        def add(self, *args): pass
        def commit(self): pass
    monkeypatch.setattr("api.middlewares.auditoria_middleware.SessionLocal", MockSession)

    resp = client.get("/api/localidades/ufs", headers={"X-System-ID": "sys_revoked", "X-API-Key": "my_valid_key"})
    assert resp.status_code == 401
    assert "X-API-Key ausente ou invalida" in resp.json()["detail"]


def test_limitador_taxa_trusted_isolated_quota(monkeypatch):
    """
    Sistemas COM API Key valida ganham cota separada (IP:System).
    """
    from core.cache import cache_service
    
    import uuid
    sys_c = f"sys_c_{uuid.uuid4().hex}"
    sys_d = f"sys_d_{uuid.uuid4().hex}"

    async def obter_cache_mock(key):
        if key == f"auth:{sys_c}":
            return "hash_valido"
        if key == f"auth:{sys_d}":
            return "hash_valido"
        return None
    monkeypatch.setattr(cache_service, "get", obter_cache_mock)
    
    import hashlib
    import hmac
    
    comparacao_original = hmac.compare_digest
    def comparacao_mock(a, b):
        if b == "hash_valido" and a == hashlib.sha256(b"my_valid_key").hexdigest():
            return True
        return comparacao_original(a, b)
    monkeypatch.setattr(hmac, "compare_digest", comparacao_mock)

    limit_str = settings.RATE_LIMIT_GLOBAL
    limit = int(limit_str.split("/")[0])

    for _ in range(limit):
        resp = client.get("/api/localidades/ufs", headers={
            "X-System-ID": sys_c,
            "X-API-Key": "my_valid_key"
        })
        assert resp.status_code == 200
        
    resp_bloqueado = client.get("/api/localidades/ufs", headers={
        "X-System-ID": sys_c,
        "X-API-Key": "my_valid_key"
    })
    assert resp_bloqueado.status_code == 429
    
    resp_d = client.get("/api/localidades/ufs", headers={
        "X-System-ID": sys_d,
        "X-API-Key": "my_valid_key"
    })
    assert resp_d.status_code == 200

def test_limitador_taxa_cep_especifico_30_por_minuto(monkeypatch):
    """
    Testa se o limitador de taxa especifico do CEP (RATE_LIMIT_CEP)
    funciona corretamente e e independente do GLOBAL.
    """
    from core.cache import cache_service
    
    import uuid
    sys_cep = f"sys_cep_{uuid.uuid4().hex}"

    async def obter_cache_mock(key):
        if key == f"auth:{sys_cep}":
            return "hash_valido"
        return None
    monkeypatch.setattr(cache_service, "get", obter_cache_mock)
    
    import hashlib
    import hmac
    
    comparacao_original = hmac.compare_digest
    def comparacao_mock(a, b):
        if b == "hash_valido" and a == hashlib.sha256(b"my_valid_key").hexdigest():
            return True
        return comparacao_original(a, b)
    monkeypatch.setattr(hmac, "compare_digest", comparacao_mock)
    
    # Precisamos mockar o ServicoCep para que ele nao tente acessar db ou cache real
    from api.services.servico_cep import ServicoCep
    async def buscar_cep_mock(self, cep):
        return {"cep": cep, "logradouro": "Rua", "localidade": "Cidade", "uf": "UF"}
    monkeypatch.setattr(ServicoCep, "buscar_cep", buscar_cep_mock)

    limit_str = settings.RATE_LIMIT_CEP
    limit = int(limit_str.split("/")[0])

    for _ in range(limit):
        resp = client.get("/api/localidades/cep/01001000", headers={
            "X-System-ID": sys_cep,
            "X-API-Key": "my_valid_key"
        })
        assert resp.status_code == 200
        
    resp_bloqueado = client.get("/api/localidades/cep/01001000", headers={
        "X-System-ID": sys_cep,
        "X-API-Key": "my_valid_key"
    })
    assert resp_bloqueado.status_code == 429
