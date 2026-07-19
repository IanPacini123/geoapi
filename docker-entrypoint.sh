#!/bin/bash
set -e

echo "Rodando migrations do banco de dados..."
alembic upgrade head

echo "Iniciando a aplicacao..."
exec "$@"
