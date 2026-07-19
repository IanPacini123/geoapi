@echo off
if "%~1"=="" (
  echo Uso: api_key.bat criar^|revogar --nome NOME_DO_SISTEMA
  exit /b 1
)

:: Roda o script de gerenciamento diretamente dentro do container da API
docker compose exec api python cli/gerenciar_sistemas.py %*
