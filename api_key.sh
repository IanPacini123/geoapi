#!/bin/bash
if [ -z "$1" ]; then
  echo "Uso: ./api_key.sh criar|revogar --nome NOME_DO_SISTEMA"
  exit 1
fi

# Roda o script de gerenciamento diretamente dentro do container da API
docker compose exec api python cli/gerenciar_sistemas.py "$@"
