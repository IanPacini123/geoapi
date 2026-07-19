from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Objeto Config do Alembic, provendo acesso aos valores do alembic.ini
config = context.config

# Interpreta o arquivo de config para configurar os loggers do Python
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

import os
import sys

# Adiciona o diretorio base (onde esta o core) ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.configuracoes import settings
from core.banco_dados import Base
# Importar os models para que o alembic os registre no Base.metadata
import core.models.ibge_models
import core.models.cep_model
import core.models.auditoria_model

# Sobrescreve a URL do banco com a do .env
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata




def run_migrations_offline() -> None:
    """Roda as migracoes em modo 'offline' (apenas gera as queries SQL sem conectar ao banco)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Roda as migracoes em modo 'online' (conectando e aplicando as queries)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
