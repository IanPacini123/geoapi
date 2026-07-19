import pytest
import json
from unittest.mock import AsyncMock, patch
from core.cache import ServicoCache

@pytest.fixture
def mock_redis():
    with patch("core.cache.redis.from_url") as mock_from_url:
        mock_client = AsyncMock()
        mock_from_url.return_value = mock_client
        yield mock_client

@pytest.fixture
def servico_cache(mock_redis):
    return ServicoCache()

@pytest.mark.asyncio
async def test_cache_get_success(servico_cache, mock_redis):
    mock_redis.get.return_value = json.dumps({"test": "data"})
    resultado = await servico_cache.get("my:key")
    
    mock_redis.get.assert_called_once_with("my:key")
    assert resultado == {"test": "data"}

@pytest.mark.asyncio
async def test_cache_get_fallback_on_error(servico_cache, mock_redis):
    mock_redis.get.side_effect = Exception("Redis connection error")
    
    resultado = await servico_cache.get("my:key")
    assert resultado is None

@pytest.mark.asyncio
async def test_cache_set_success(servico_cache, mock_redis):
    resultado = await servico_cache.set("my:key", {"test": "data"})
    
    mock_redis.set.assert_called_once()
    assert resultado is True

@pytest.mark.asyncio
async def test_cache_set_fallback_on_error(servico_cache, mock_redis):
    mock_redis.set.side_effect = Exception("Redis connection error")
    
    resultado = await servico_cache.set("my:key", {"test": "data"})
    assert resultado is False

@pytest.mark.asyncio
async def test_cache_delete_pattern(servico_cache, mock_redis):
    async def mock_scan_iter(match=None):
        for key in ["key1", "key2"]:
            yield key
            
    mock_redis.scan_iter = mock_scan_iter
    
    resultado = await servico_cache.deletar_padrao("my:*")
    
    assert mock_redis.delete.call_count == 2
    assert resultado is True
