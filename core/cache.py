import json
import logging
from typing import Any, Optional
import redis.asyncio as redis
from core.configuracoes import settings

logger = logging.getLogger(__name__)

class ServicoCache:
    def __init__(self):
        self.cliente_redis: Optional[redis.Redis] = None

    def _get_redis(self):
        if self.cliente_redis is None:
            try:
                self.cliente_redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
            except Exception as e:
                logger.error(f"Falha ao inicializar o cliente Redis: {e}")
        return self.cliente_redis

    async def get(self, key: str) -> Optional[Any]:
        r = self._get_redis()
        if not r:
            return None
        try:
            val = await r.get(key)
            return json.loads(val) if val else None
        except Exception as e:
            logger.warning(f"Falha no GET do Redis para a chave {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        r = self._get_redis()
        if not r:
            return False
        try:
            await r.set(key, json.dumps(value), ex=ex)
            return True
        except Exception as e:
            logger.warning(f"Falha no SET do Redis para a chave {key}: {e}")
            return False

    async def deletar_padrao(self, padrao: str) -> bool:
        r = self._get_redis()
        if not r:
            return False
        try:
            deletados = 0
            async for key in r.scan_iter(match=padrao):
                await r.delete(key)
                deletados += 1
            return True
        except Exception as e:
            logger.warning(f"Redis DELETE padrao failed for {padrao}: {e}")
            return False

cache_service = ServicoCache()
