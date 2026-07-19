import time
import datetime
import logging
from sqlalchemy import text
from core.banco_dados import SessionLocal
from cli.sincronizar_dados import main as sincronizar

# Setup basico de log para substituir o print (mantendo consistencia)
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
logger = logging.getLogger(__name__)

def sleep_until_midnight():
    """Calcula os segundos restantes ate a proxima meia-noite e dorme."""
    now = datetime.datetime.now()
    tomorrow = now + datetime.timedelta(days=1)
    midnight = datetime.datetime(
        year=tomorrow.year, month=tomorrow.month, day=tomorrow.day,
        hour=0, minute=0, second=0
    )
    seconds_to_wait = (midnight - now).total_seconds()
    logger.info(f"Dormindo por {int(seconds_to_wait)} segundos ate a proxima meia-noite (00:00)...")
    time.sleep(seconds_to_wait)

def wait_for_migrations():
    """Trava a execucao inicial ate que o schema oficial do banco seja criado pelo Alembic."""
    logger.info("Aguardando as migracoes do banco (Alembic) finalizarem...")
    while True:
        try:
            with SessionLocal() as db:
                # Se a tabela 'uf' oficial existir, significa que o Alembic rodou.
                result = db.execute(text("SELECT to_regclass('public.uf');")).scalar()
                if result:
                    logger.info("Migracoes detectadas! Banco de dados pronto.")
                    return
        except Exception:
            pass
        logger.info("O banco ainda nao foi estruturado. Aguardando 5 segundos...")
        time.sleep(5)

def run_scheduler():
    logger.info("Iniciando Agendador de Sincronizacao Automatica do IBGE...")
    
    # 0. Trava de Seguranca: Garante que o desenvolvedor ou CI/CD tenha rodado o Alembic
    wait_for_migrations()
    
    # 1. Execucao Imediata na Subida do Container
    try:
        logger.info("Executando primeira sincronizacao imediatamente na subida do sistema...")
        sincronizar()
        logger.info("Sincronizacao inicial concluida com sucesso!")
    except Exception as e:
        logger.error(f"Erro durante a sincronizacao inicial: {e}")
        logger.info("Apesar do erro, o agendador continuara ativo.")
        
    # 2. Execucao Diaria a Meia-Noite (00:00)
    while True:
        try:
            # Sempre espera bater 00:00 antes de agir
            sleep_until_midnight()
            
            logger.info("Acionando sincronizacao do IBGE diaria (00:00)...")
            sincronizar()
            logger.info("Sincronizacao diaria concluida com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro durante a sincronizacao diaria: {e}")
            logger.info("Ocorreu uma falha. A proxima tentativa sera na proxima meia-noite.")
            # O laco reinicia imediatamente, chamando sleep_until_midnight()

if __name__ == "__main__":
    run_scheduler()
