# API GeoCEP

Uma API robusta e de alta performance desenvolvida com **FastAPI** para consultar e enriquecer dados de enderecos e localidades geograficas, baseada fortemente na arquitetura de software **Domain-Driven Design (DDD)**.

Este projeto busca trazer resiliencia as aplicacoes utilizando a estrategia **API-First com Fallback e Upsert**. Ele consome, sincroniza e armazena os metadados oficias do **IBGE** (Regioes, Estados, Mesorregioes, Municipios, etc) no banco de dados local para enriquecer as consultas de CEP com as conhecidas *Natural Keys* (codigo M49 e codigos do IBGE).

---

##  Principais Funcionalidades

- **Consulta Resiliente de CEP (API-First + Fallback)**: Ao buscar um CEP, o sistema tenta acessa-lo primeiramente na internet para obter a versao mais fresca possivel. Se as APIs governamentais estiverem fora do ar, a requisicao devolve o ultimo estado salvo no nosso banco de dados local (*Cold Storage*).
- **Protecao Contra Abusos (Rate Limiting e CORS)**: A API utiliza `slowapi` limitando 100 requisicoes por minuto por IP (sendo 30/min no endpoint dinamico de CEP). Isso **protege proativamente as APIs de fallback (BrasilAPI/ViaCEP)** contra o esgotamento de suas cotas gratuitas causado por requisicoes em massa, alem de possuir CORS strict habilitado via variavel de ambiente `ALLOWED_ORIGINS`.
- **Upsert Inteligente**: Caso o CEP seja retornado pela API externa, nos comparamos a resposta com o que temos armazenado no banco local. Se houver alguma mudanca governamental (ex: nome da rua alterou), a API atualiza o banco local silenciosamente (*Upsert*).
- **Sincronizacao Inteligente com o IBGE**: Um CLI nativo (`cli/sincronizar_dados.py`) responsavel por se conectar aos servicos oficias do IBGE, gerar `.csv`s da vigencia atual e aplicar um *Diff* assincrono (*merge* via Pandas) salvando as mudancas e atualizacoes geograficas no PostgreSQL.
- **Enriquecimento de Dados**: Alem do Logradouro e Bairro, as consultas de CEP retornam os respectivos IDs oficiais (Codigos IBGE) do Estado e do Municipio atrelados aquele codigo postal.
- **Auditoria Transparente (Zero-Trust Self-Hosted)**: Este projeto e distribuido como uma API self-hosted de codigo aberto. Quem sobe a instancia gerencia suas proprias chaves. Um Middleware intercepta 100% das requisicoes realizadas. Utilizando a identificacao via *Header* (`X-System-ID` e `X-API-Key`), o sistema exige autenticacao em todos os endpoints, bloqueia acessos indevidos e grava silenciosamente no banco qual microsservico/usuario fez o acesso com prova criptografica.

---

##  Tecnologias e Stack

- **Python 3.12**
- **FastAPI** (Web Framework Assincrono)
- **SQLAlchemy & Alembic** (ORM e Controle de Migracoes)
- **PostgreSQL 15** (Banco de Dados Relacional principal)
- **Redis** (Camada de Cache-aside em Memoria)
- **Pandas** (ETL e Sincronizacao Inteligente de CSVs)
- **Docker & Docker Compose** (Containerizacao Completa)
- **Gunicorn + Uvicorn** (Servidor de Producao Multi-worker)
---

##  Arquitetura em Camadas

O projeto foi refatorado para manter uma rigida separacao de responsabilidades:

- `/api`: Camada de Apresentacao e Aplicacao. Contem os **Routers** (endpoints), **Middlewares** (Auditoria), **Schemas** (Pydantic DTOs), e **Services** (logica de negocio isolada como o *Cache-aside*).
- `/core`: Camada de Dominio e Infraestrutura. Mantem a conexao com o banco de dados via SQLAlchemy e armazena a modelagem oficial (`models`) baseada em *Surrogate Keys*.
- `/cli`: Rotinas de *Command Line*. Ficam isolados os scripts extratores do IBGE (`callers`) e a nossa joia: o orquestrador `sincronizar_dados.py`.
- `/data`: Camada de *Storage* local que guarda os arquivos `.csv` estaticos vigentes para efeito de comparacao (Diff) futura.

> **Nota Tecnica (Melhoria Futura):** Os 8 routers do IBGE (paises, regioes, estados, municipios, etc.) compartilham uma alta duplicacao de codigo estrutural (fluxo identico de Cache MISS/HIT e paginacao). A logica de cache foi verificada de forma automatizada (via mocks e spies no DB) em 3 dominios representativos (Municipios, UFs, Paises) e testada manualmente com o `MONITOR` real do Redis em pelo menos 1 (Mesorregioes). Como os demais compartilham exatamente a mesma implementacao estrutural, optou-se por nao estender a verbosidade de testes unitarios de cache para todos os 8 dominios. Em futuras refatoracoes, uma classe base de Factory (ex: `GenericIBGERouter`) poderia instanciar essas rotas dinamicamente, reduzindo drasticamente esse *boilerplate*.
>
> **Nota Tecnica (Falha Conhecida / Proxies):** Caso a API seja exposta atras de um Proxy Reverso ou Load Balancer (como AWS ALB, Nginx), o Rate Limit vai bloquear todos os usuarios de forma agressiva. Isso ocorre porque o Gunicorn/Uvicorn enxergara apenas o IP interno do Proxy. Para resolver, sera necessario adicionar a flag `--forwarded-allow-ips="*"` no comando de inicializacao do Dockerfile.
>
> > [!WARNING]
> > **AVISO DE SEGURANCA:** A flag `--forwarded-allow-ips="*"` **so deve ser usada se a API estiver genuinamente atras de um proxy confiavel** que sobrescreve o header `X-Forwarded-For` do cliente. Se a API for exposta diretamente a internet sem proxy e com essa flag ativada, qualquer requisicao maliciosa podera forjar seu proprio IP enviando esse header, contornando completamente o rate limit por IP.
>
> **Nota Tecnica (Cache Negativo de Autenticacao):** Atualmente, o Middleware de Auditoria aplica cache local em memoria (LRU) apenas para sistemas *autorizados* para evitar bater no banco (PostgreSQL) a cada requisicao. Porem, nao existe um "Cache Negativo" para falhas consecutivas. Uma melhoria futura de *Hardening* seria registrar acessos negados no Redis, barrando floods de brute-force ou chaves invalidas na borda, aliviando a CPU.
>
> **Nota Tecnica (CORS / Testes Automatizados):** A logica de parsing da variavel de ambiente `ALLOWED_ORIGINS` no `api/main.py` esta validada manualmente (via curl, na Camada 6 desta auditoria), mas nao possui teste automatizado dedicado. O teste `test_cors_preflight_without_auth` usa um mock direto na funcao `is_allowed_origin` da biblioteca subjacente para garantir resiliencia de ambiente, em vez de exercitar o nosso parsing real do `.env`.
>
> **Nota Tecnica (Mutation Testing):** Para garantir o maximo rigor da suite de testes unitarios contra falsos-positivos de cobertura de codigo, uma das evolucoes planejadas e a incorporacao do `mutmut` para Teste de Mutacao. Em ambientes Windows via WSL, a execucao pode exigir configuracoes especificas de *sys_ptrace* ou isolamento, motivo pelo qual essa melhoria foi protelada.

---

##  Como Executar e Testar

### 1. Requisitos e Setup (.env)
Antes de subir os containers, copie o arquivo `.env.example` para `.env` e preencha conforme necessario. A aplicacao possui politica de *Fail-Secure*, exigindo que variaveis sensiveis sejam explicitas:
- `POSTGRES_PASSWORD`: Obrigatorio (senha do banco).
- `ALLOWED_ORIGINS`: Lista de dominios para o CORS (ex: `http://localhost:3000`).
- `REDIS_URL`: URL de conexao do Cache.
- `RATE_LIMIT_GLOBAL`: Limite de requisicoes global da API (padrao: `100/minute`).
- `RATE_LIMIT_CEP`: Limite de requisicoes para busca de CEPs (padrao: `30/minute`).
- `RATE_LIMIT_OPTIONS`: Limite para preflight CORS (OPTIONS) por IP (padrao: `300/minute`).

### 2. Subindo a Infraestrutura (Docker)

**Para Desenvolvimento (Local):**
Na sua maquina local (onde voce precisa subir o banco de dados e o cache embutidos), rode o projeto ativando o **profile dev**:
```bash
docker-compose --profile dev up -d --build
```
Isso subira o PostgreSQL (`db`) na porta 5436, o Redis (`cache`) operando de forma 100% interna na rede do Docker, a API FastAPI de producao (`api`) usando Gunicorn, e o Job de Sincronizacao (`sync_job`).

**Para Producao:**
Os containers de banco e cache estao isolados no profile `dev`. Se voce for rodar em producao e ja possuir esses servicos hospedados em outro servidor, forneca as credenciais via `.env` e rode sem o profile:
```bash
export POSTGRES_HOST=meu-banco-producao.com
export POSTGRES_USER=meu-usuario
export POSTGRES_PASSWORD=minha-senha
docker-compose up -d --build
```
Neste cenario, apenas a `api` e o `sync_job` serao inicializados.

### 3. Sincronizacao Automatica (Cron Job)
O proprio `docker-compose` gerencia a vida util de um *container* chamado `sync_job`.
Ao rodar, ele automaticamente invocara o script `cli/scheduler.py` em background. Ele fara a primeira sincronizacao do IBGE de imediato e, depois, dormira silenciosamente por 30 dias.

Se por algum motivo quiser forcar uma sincronizacao manual:
```bash
docker exec localidade_api python cli/sincronizar_dados.py
```

### 4. Gerenciamento de Sistemas (API Keys)
O projeto usa uma filosofia de **Zero-Trust (Confianca Zero)**.
Sistemas anonimos (sem chave) sao sumariamente **bloqueados** (HTTP 401) pelo Middleware. Qualquer sistema consumidor **deve** possuir uma credencial valida. Sistemas autenticados ganham um pool de rate limit isolado.

Para criar uma chave de alta entropia para um novo cliente (rodar no servidor):
```bash
# No Linux/Mac (Bash):
./api_key.sh criar --nome="meu_frontend"

# No Windows (CMD/PowerShell):
api_key.bat criar --nome="meu_frontend"
```

*O console exibira a `X-API-Key` apenas uma vez. O banco de dados armazena apenas o Hash SHA-256 da chave.*

Para revogar o acesso (mantendo o historico de auditoria e invalidando o cache em tempo real):
```bash
# No Linux/Mac (Bash):
./api_key.sh revogar --nome="meu_frontend"

# No Windows (CMD/PowerShell):
api_key.bat revogar --nome="meu_frontend"
```

**Uso no Swagger UI:**
Acessando a documentacao iterativa em `http://localhost:8000/docs`, voce vera um botao **Authorize** no canto superior direito. Ao clicar nele, voce devera preencher dois campos:
- **X-System-ID**: O nome do sistema (ex: "meu_frontend")
- **X-API-Key**: A chave gerada pelo CLI.
Apos autorizar, voce podera testar todas as rotas diretamente pelo navegador.

### 5. Quick Start (Exemplos de Uso)

A API **exige obrigatoriamente** os cabecalhos `X-System-ID` e `X-API-Key` em todas as rotas de dados (com excecao do Swagger UI). Falhar em prove-los resultara em `401 Unauthorized`.

**Exemplo via cURL (Busca de CEP com API Key):**
```bash
curl -X GET "http://localhost:8000/api/localidades/cep/01001000" \
     -H "X-System-ID: meu_frontend" \
     -H "X-API-Key: <CHAVE_GERADA_PELA_CLI>"
```

**Exemplo via Python/Requests (Listar UFs com Cache):**
```python
import requests

url = "http://localhost:8000/api/localidades/ufs"
headers = {
    "X-System-ID": "script_automacao",
    "X-API-Key": "sua_chave_gerada"
}

response = requests.get(url, headers=headers)
print(response.json())
```

### 6. Utilizando a API
A API estara disponivel em `http://localhost:8000`. O *Swagger UI* interativo pode ser acessado em `http://localhost:8000/docs`.

Para a especificacao tecnica detalhada, parametros, fluxos e contratos JSON (ideal para uso de LLMs e Frontends), consulte o arquivo **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)**.

#### Endpoints Principais:

**Buscar CEP:**
- `GET /api/localidades/cep/{cep}`
- **Headers Necessarios:** `X-System-ID` (ex: "nome_do_meu_sistema") e `X-API-Key`
- **Exemplo de Retorno:**
```json
{
  "cep": "01001000",
  "logradouro": "Praca da Se",
  "bairro": "Se",
  "localidade": "Sao Paulo",
  "uf": "SP",
  "uf_codigo": 35,
  "municipio_codigo": 3550308,
  "tipo_logradouro_codigo": null,
  "data_criacao": "2026-06-26T14:05:23.935439"
}
```

**Consultar Estados (UFs):**
- `GET /api/localidades/ufs`
- **Exemplo de Retorno (Array de Objetos):**
```json
[
  {
    "id": 1,
    "codigo_ibge": 11,
    "sigla": "RO",
    "nome": "Rondonia"
  },
  ...
]
```

**Consultar Estados (UFs) por Regiao:**
- `GET /api/localidades/ufs/regiao/{regiao_sigla}`
- **Parametro de Path:** `regiao_sigla` (ex: "NE", "SE", "S")

**Buscar Entidades por ID IBGE (Natural Key):**
- Todas as entidades suportam busca pelo codigo IBGE exato:
- `GET /api/localidades/municipios/codigo/{codigo_ibge}`
- `GET /api/localidades/ufs/codigo/{codigo_ibge}`

**Busca Textual Tolerante (Fuzzy Search):**
- Todas as entidades possuem um endpoint para busca com nomes incompletos ou "sujos" (*Case-Insensitive*):
- `GET /api/localidades/municipios/nome/{nome}` (Retorna um Array)
- `GET /api/localidades/ufs/nome/{nome}`

**Validacao em Lote (Batch Validation):**
- Validacao simultanea e otimizada de multiplos codigos IBGE para persistencia em lote:
- `POST /api/localidades/validate-batch`

**Consultar Todos os Municipios:**
- `GET /api/localidades/municipios`

**Consultar Municipios de um Estado:**
- `GET /api/localidades/municipios/{uf_sigla}`
- **Parametro de Path:** `uf_sigla` (ex: "SP", "RJ", "MG")
- **Exemplo de Retorno (Array de Objetos):**
```json
[
  {
    "id": 4854,
    "codigo_ibge": 3550308,
    "nome": "Sao Paulo"
  },
  ...
]
```

**Consultar Municipios por Regiao:**
- `GET /api/localidades/municipios/regiao/{regiao_sigla}`
- **Parametro de Path:** `regiao_sigla` (ex: "NE", "SE", "S")

---
*Projeto idealizado e desenvolvido como servico base de localidade georreferenciada.*
