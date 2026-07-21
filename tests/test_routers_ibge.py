import pytest
from fastapi.testclient import TestClient
from api.main import app
from unittest.mock import MagicMock, patch
from core.banco_dados import obter_bd
from core.models.ibge_models import Municipio, Uf
import json
client = TestClient(app)

@pytest.fixture(autouse=True)
def servico_cache_mock(monkeypatch):
    """
    Mock do cache_service simulando o Redis em memoria para evitar erro de Event Loop do TestClient.

    Parametros:
        monkeypatch: Fixture do pytest usada para aplicar os patches.

    Gera:
        ServicoCache: A instancia mockada do cache_service.

    Mocks the cache_service simulating Redis in memory to avoid a TestClient Event Loop error.

    Args:
        monkeypatch: The pytest fixture used to apply the patches.

    Yields:
        ServicoCache: The mocked cache_service instance.
    """
    from core.cache import cache_service
    import hashlib
    hash_esperado = hashlib.sha256(b"test_key").hexdigest()

    cache_store = {}
    async def mock_get(key): 
        if str(key).startswith("auth:"): return hash_esperado
        return cache_store.get(key)
    async def mock_set(key, value, expire=None): cache_store[key] = value

    with patch.object(cache_service, 'get', side_effect=mock_get), \
         patch.object(cache_service, 'set', side_effect=mock_set):
        yield cache_service



def test_municipios_cache_flow(db_session_memory):
    # Prepara o banco de dados em memoria
    mock_municipio = Municipio(codigo_ibge=3550308, nome="Sao Paulo")
    db_session_memory.add(mock_municipio)
    db_session_memory.commit()

    # Sobrescreve a dependencia para usar o banco em memoria
    app.dependency_overrides[obter_bd] = lambda: db_session_memory
    
    with patch.object(db_session_memory, 'query', wraps=db_session_memory.query) as spy_query:
        try:
            # 1. Primeira chamada: CACHE MISS (deve ir ao banco)
            response1 = client.get("/api/localidades/municipios", headers={"X-System-ID": "test", "X-API-Key": "test_key"})
            assert response1.status_code == 200
            dados1 = response1.json()
            assert len(dados1) == 1
            assert dados1[0]["nome"] == "Sao Paulo"
            
            # Garante que o banco de dados foi consultado
            spy_query.assert_called()
            
            # Limpamos a tabela no banco so para ter 100% de certeza que a rota nao vai ler do SQLite
            db_session_memory.query(Municipio).delete()
            db_session_memory.commit()
            
            # Reseta o spy para a proxima checagem (DEPOIS de limpar o banco)
            spy_query.reset_mock()

            # 2. Segunda chamada: CACHE HIT (NAO deve ir ao banco)
            response2 = client.get("/api/localidades/municipios", headers={"X-System-ID": "test", "X-API-Key": "test_key"})
            assert response2.status_code == 200
            dados2 = response2.json()
            assert len(dados2) == 1
            assert dados2[0]["nome"] == "Sao Paulo"
            
            # Prova real que o banco de dados foi completamente evitado pelo cache
            spy_query.assert_not_called()
        finally:
            app.dependency_overrides.clear()

def test_ufs_cache_flow(db_session_memory):
    # Prepara o banco de dados em memoria
    mock_uf = Uf(codigo_ibge=35, sigla="SP", nome="Sao Paulo")
    db_session_memory.add(mock_uf)
    db_session_memory.commit()
    
    app.dependency_overrides[obter_bd] = lambda: db_session_memory
    with patch.object(db_session_memory, 'query', wraps=db_session_memory.query) as spy_query:
        try:
            # CACHE MISS
            response1 = client.get("/api/localidades/ufs", headers={"X-System-ID": "test", "X-API-Key": "test_key"})
            assert response1.status_code == 200
            dados1 = response1.json()
            assert len(dados1) == 1
            
            spy_query.assert_called()
            spy_query.reset_mock()
            
            # CACHE HIT
            response2 = client.get("/api/localidades/ufs", headers={"X-System-ID": "test", "X-API-Key": "test_key"})
            assert response2.status_code == 200
            dados2 = response2.json()
            assert len(dados2) == 1
            assert dados2[0]["nome"] == "Sao Paulo"
            
            spy_query.assert_not_called()
        finally:
            app.dependency_overrides.clear()

def test_paises_cache_flow(db_session_memory):
    from core.models.ibge_models import Pais
    # Prepara o banco de dados em memoria
    mock_pais = Pais(codigo_ibge=76, nome="Brasil")
    db_session_memory.add(mock_pais)
    db_session_memory.commit()
    
    app.dependency_overrides[obter_bd] = lambda: db_session_memory
    with patch.object(db_session_memory, 'query', wraps=db_session_memory.query) as spy_query:
        try:
            # 1. Primeira chamada: CACHE MISS
            response1 = client.get("/api/localidades/paises", headers={"X-System-ID": "test", "X-API-Key": "test_key"})
            assert response1.status_code == 200
            dados1 = response1.json()
            assert len(dados1) == 1
            
            spy_query.assert_called()
            
            # Deletar do banco para provar o cache
            db_session_memory.query(Pais).delete()
            db_session_memory.commit()
            
            spy_query.reset_mock()
            
            # 2. Segunda chamada: CACHE HIT
            response2 = client.get("/api/localidades/paises", headers={"X-System-ID": "test", "X-API-Key": "test_key"})
            assert response2.status_code == 200
            dados2 = response2.json()
            assert len(dados2) == 1
            assert dados2[0]["nome"] == "Brasil"
            
            spy_query.assert_not_called()
        finally:
            app.dependency_overrides.clear()

def test_municipios_paginacao(db_session_memory):
    # Insere 15 municipios
    for i in range(1, 16):
        db_session_memory.add(Municipio(codigo_ibge=3550300 + i, nome=f"Municipio {i}"))
    db_session_memory.commit()

    app.dependency_overrides[obter_bd] = lambda: db_session_memory
    try:
        # Testa limit=10
        response = client.get("/api/localidades/municipios?skip=0&limit=10", headers={"X-System-ID": "test", "X-API-Key": "test_key"})
        assert response.status_code == 200
        dados = response.json()
        assert len(dados) == 10
        
        # Testa skip=10, limit=10 (deve retornar os 5 restantes)
        response2 = client.get("/api/localidades/municipios?skip=10&limit=10", headers={"X-System-ID": "test", "X-API-Key": "test_key"})
        assert response2.status_code == 200
        dados2 = response2.json()
        assert len(dados2) == 5
    finally:
        app.dependency_overrides.clear()

def test_buscar_municipio_nome_invalido_200_vazio(db_session_memory):
    # Mesmo com banco vazio, a busca fuzzy deve retornar 200 OK com array vazio, e nao 404
    app.dependency_overrides[obter_bd] = lambda: db_session_memory
    try:
        response = client.get("/api/localidades/municipios/nome/NomeInvalidoQueNaoExiste", headers={"X-System-ID": "test", "X-API-Key": "test_key"})
        assert response.status_code == 200
        assert response.json() == []
    finally:
        app.dependency_overrides.clear()
