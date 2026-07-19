FROM python:3.12-slim

WORKDIR /app

# Instala dependências do SO (se houver alguma no futuro)
# RUN apt-get update && apt-get install -y <package> && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do projeto
COPY . .

# Expõe a porta 8000
EXPOSE 8000

# Adiciona o diretório atual ao PYTHONPATH para que os módulos core e api sejam encontrados
ENV PYTHONPATH=/app

# Default worker count for Gunicorn
ENV WEB_CONCURRENCY=4

# Configura o entrypoint
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]

# Inicia o Gunicorn com Uvicorn workers
CMD ["sh", "-c", "gunicorn api.main:app -w ${WEB_CONCURRENCY} -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000"]
