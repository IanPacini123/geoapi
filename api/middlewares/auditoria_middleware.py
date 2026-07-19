from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from core.banco_dados import SessionLocal
from core.models.auditoria_model import AuditoriaRequisicao
from datetime import datetime

class AuditoriaMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            try:
                from core.cache import cache_service
                from core.configuracoes import settings
                
                limit_str = settings.RATE_LIMIT_OPTIONS.split("/")[0]
                limit = int(limit_str) if limit_str.isdigit() else 300
                
                client_ip = request.client.host if request.client else "unknown"
                flood_key = f"options_flood:{client_ip}"
                
                r = cache_service._get_redis()
                if r:
                    current_count = await r.incr(flood_key)
                    if current_count == 1:
                        await r.expire(flood_key, 60)
                    
                    if current_count > limit:
                        from fastapi.responses import JSONResponse
                        return JSONResponse(status_code=429, content={"detail": "Too Many Requests"})
            except Exception as e:
                print(f"Erro no rate limit do OPTIONS (fail-open): {e}")
                
            return await call_next(request)

        tempo_inicio = datetime.utcnow()
        sistema = request.headers.get("x-system-id")
        if not sistema:
            if request.url.path.startswith("/api/"):
                from fastapi.responses import JSONResponse
                return JSONResponse(status_code=401, content={"detail": "Cabecalho X-System-ID obrigatorio"})
            else:
                sistema = "desconhecido"

        request.state.is_trusted_system = False
        chave_api = request.headers.get("x-api-key")

        if sistema and sistema != "desconhecido" and chave_api:
            from core.cache import cache_service
            from core.models.sistema_autorizado_model import SistemaAutorizado
            import hashlib
            import hmac
            
            chave_cache = f"auth:{sistema}"
            hash_em_cache = await cache_service.get(chave_cache)
            
            if not hash_em_cache:
                bd_auth = SessionLocal()
                try:
                    sistema_db = bd_auth.query(SistemaAutorizado).filter(
                        SistemaAutorizado.nome_sistema == sistema,
                        SistemaAutorizado.ativo == True
                    ).first()
                    
                    if sistema_db:
                        hash_em_cache = sistema_db.chave_hash
                        await cache_service.set(chave_cache, hash_em_cache, ex=60)
                finally:
                    bd_auth.close()
            
            if hash_em_cache:
                hash_recebido = hashlib.sha256(chave_api.encode('utf-8')).hexdigest()
                if hmac.compare_digest(hash_recebido, hash_em_cache):
                    request.state.is_trusted_system = True

        if request.url.path.startswith("/api/") and not request.state.is_trusted_system:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=401, 
                content={"detail": "Acesso negado. X-API-Key ausente ou invalida."}
            )

        try:
            response: Response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise e
        finally:
            try:
                db = SessionLocal()
                auditoria = AuditoriaRequisicao(
                    sistema_usuario=sistema,
                    endpoint=request.url.path,
                    metodo=request.method,
                    data_hora=tempo_inicio,
                    status_code=status_code
                )
                db.add(auditoria)
                db.commit()
            except Exception as e:
                print(f"Erro ao salvar auditoria: {e}")
            finally:
                db.close()
                
        return response
