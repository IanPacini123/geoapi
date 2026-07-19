import argparse
import secrets
import hashlib
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import sys
import os

# Adiciona o diretorio raiz ao PYTHONPATH para os imports funcionarem
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.banco_dados import SessionLocal
from core.models.sistema_autorizado_model import SistemaAutorizado

def gerar_hash_chave(api_key: str) -> str:
    return hashlib.sha256(api_key.encode('utf-8')).hexdigest()

def criar_sistema(nome: str, db: Session):
    # Gera uma chave de alta entropia (32 bytes = 256 bits)
    chave_bruta = secrets.token_urlsafe(32)
    chave_em_hash = gerar_hash_chave(chave_bruta)

    sistema = SistemaAutorizado(
        nome_sistema=nome,
        chave_hash=chave_em_hash,
        ativo=True
    )
    
    try:
        db.add(sistema)
        db.commit()
        print(f"Sistema '{nome}' criado com sucesso!")
        print(f"=== ATENCAO: GUARDE ESTA CHAVE AGORA ===")
        print(f"Ela nao sera exibida novamente.")
        print(f"X-API-Key: {chave_bruta}")
        print(f"========================================")
    except IntegrityError:
        db.rollback()
        print(f"Erro: Ja existe um sistema com o nome '{nome}'.")
        sys.exit(1)

def revogar_sistema(nome: str, db: Session):
    sistema = db.query(SistemaAutorizado).filter(SistemaAutorizado.nome_sistema == nome).first()
    
    if not sistema:
        print(f"Erro: Sistema '{nome}' nao encontrado.")
        sys.exit(1)
        
    if not sistema.ativo:
        print(f"Aviso: O sistema '{nome}' ja esta inativo.")
        return
        
    sistema.ativo = False
    db.commit()
    
    # Invalida o cache em tempo real
    import asyncio
    from core.cache import cache_service
    
    async def limpar_cache():
        await cache_service.deletar_padrao(f"auth:{nome}")
        if cache_service.cliente_redis:
            await cache_service.cliente_redis.aclose()
            
    asyncio.run(limpar_cache())
    
    print(f"Sistema '{nome}' revogado com sucesso. O rate limit isolado dele foi cancelado e o cache foi limpo.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gerenciador de Sistemas Autorizados (API Keys)")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    # Comando Criar
    parser_criar = subparsers.add_parser("criar", help="Cria um novo sistema autorizado")
    parser_criar.add_argument("--nome", required=True, help="Nome do sistema (X-System-ID)")

    # Comando Revogar
    parser_revogar = subparsers.add_parser("revogar", help="Revoga um sistema autorizado")
    parser_revogar.add_argument("--nome", required=True, help="Nome do sistema a ser revogado")

    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.comando == "criar":
            criar_sistema(args.nome, db)
        elif args.comando == "revogar":
            revogar_sistema(args.nome, db)
    finally:
        db.close()
