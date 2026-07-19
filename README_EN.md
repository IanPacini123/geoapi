# API GeoCEP

[🇧🇷 Português](./README.md) | 🇺🇸 English

A robust and high-performance API developed with **FastAPI** to query and enrich geographic address and location data, strongly based on the **Domain-Driven Design (DDD)** software architecture.

This project aims to bring resilience to applications using an **API-First with Fallback and Upsert** strategy. It consumes, synchronizes, and stores official metadata from **IBGE** (Regions, States, Mesoregions, Municipalities, etc.) in the local database to enrich CEP (postal code) queries with well-known *Natural Keys* (M49 code and IBGE codes).

---

##  Main Features

- **Resilient CEP Query (API-First + Fallback)**: When searching for a CEP, the system first tries to access it on the internet to get the freshest possible version. If the government APIs are offline, the request returns the latest state saved in our local database (*Cold Storage*).
- **Abuse Protection (Rate Limiting and CORS)**: The API uses `slowapi` limiting 100 requests per minute per IP (being 30/min in the dynamic CEP endpoint). This **proactively protects the fallback APIs (BrasilAPI/ViaCEP)** against the depletion of their free quotas caused by mass requests, besides having strict CORS enabled via the `ALLOWED_ORIGINS` environment variable.
- **Smart Upsert**: If the CEP is returned by the external API, we compare the response with what we have stored in the local database. If there is any government change (e.g., street name changed), the API updates the local database silently (*Upsert*).
- **Smart Synchronization with IBGE**: A native CLI (`cli/sincronizar_dados.py`) responsible for connecting to official IBGE services, generating `.csv`s of the current validity and applying an asynchronous *Diff* (*merge* via Pandas) saving the changes and geographic updates in PostgreSQL.
- **Data Enrichment**: Besides the Street and Neighborhood, CEP queries return the respective official IDs (IBGE Codes) of the State and Municipality linked to that postal code.
- **Transparent Auditing (Zero-Trust Self-Hosted)**: This project is distributed as an open-source self-hosted API. Whoever spins up the instance manages their own keys. A Middleware intercepts 100% of the requests made. Using identification via *Header* (`X-System-ID` and `X-API-Key`), the system requires authentication in all endpoints, blocks unauthorized access and silently records in the database which microservice/user made the access with cryptographic proof.

---

##  Technologies and Stack

- **Python 3.12**
- **FastAPI** (Asynchronous Web Framework)
- **SQLAlchemy & Alembic** (ORM and Migrations Control)
- **PostgreSQL 15** (Main Relational Database)
- **Redis** (In-Memory Cache-aside Layer)
- **Pandas** (ETL and Smart Synchronization of CSVs)
- **Docker & Docker Compose** (Full Containerization)
- **Gunicorn + Uvicorn** (Multi-worker Production Server)
---

##  Layered Architecture

The project was refactored to maintain a strict separation of concerns:

- `/api`: Presentation and Application Layer. Contains the **Routers** (endpoints), **Middlewares** (Auditing), **Schemas** (Pydantic DTOs), and **Services** (isolated business logic like *Cache-aside*).
- `/core`: Domain and Infrastructure Layer. Maintains the database connection via SQLAlchemy and stores the official modeling (`models`) based on *Surrogate Keys*.
- `/cli`: *Command Line* routines. The IBGE extractor scripts (`callers`) and our crown jewel: the orchestrator `sincronizar_dados.py` are isolated here.
- `/data`: Local *Storage* layer that keeps the current static `.csv` files for future comparison (Diff) purposes.

> **Technical Note (Future Improvement):** The 8 IBGE routers (countries, regions, states, municipalities, etc.) share a high structural code duplication (identical flow of Cache MISS/HIT and pagination). The cache logic was verified automatically (via mocks and spies in the DB) in 3 representative domains (Municipalities, UFs, Countries) and tested manually with the real Redis `MONITOR` in at least 1 (Mesoregions). As the others share exactly the same structural implementation, it was decided not to extend the verbosity of cache unit tests to all 8 domains. In future refactorings, a Factory base class (e.g., `GenericIBGERouter`) could instantiate these routes dynamically, drastically reducing this *boilerplate*.
>
> **Technical Note (Known Flaw / Proxies):** If the API is exposed behind a Reverse Proxy or Load Balancer (like AWS ALB, Nginx), the Rate Limit will block all users aggressively. This occurs because Gunicorn/Uvicorn will only see the internal IP of the Proxy. To solve this, it will be necessary to add the `--forwarded-allow-ips="*"` flag in the Dockerfile initialization command.
>
> > [!WARNING]
> > **SECURITY WARNING:** The `--forwarded-allow-ips="*"` flag **should only be used if the API is genuinely behind a trusted proxy** that overwrites the client's `X-Forwarded-For` header. If the API is exposed directly to the internet without a proxy and with this flag enabled, any malicious request will be able to forge its own IP by sending this header, completely bypassing the IP rate limit.
>
> **Technical Note (Authentication Negative Cache):** Currently, the Auditing Middleware applies local in-memory cache (LRU) only for *authorized* systems to avoid hitting the database (PostgreSQL) on every request. However, there is no "Negative Cache" for consecutive failures. A future *Hardening* improvement would be to register denied accesses in Redis, blocking brute-force floods or invalid keys at the edge, relieving the CPU.
>
> **Technical Note (CORS / Automated Tests):** The parsing logic of the `ALLOWED_ORIGINS` environment variable in `api/main.py` is manually validated (via curl simulating a real browser preflight request), but does not have a dedicated automated test. The `test_cors_preflight_without_auth` test uses a direct mock on the `is_allowed_origin` function of the underlying library to ensure environment resilience, instead of exercising our real `.env` parsing.
>
> **Technical Note (Mutation Testing):** To ensure the maximum rigor of the unit test suite against code coverage false positives, one of the planned evolutions is the incorporation of `mutmut` for Mutation Testing. In Windows environments via WSL, the execution may require specific *sys_ptrace* configurations or isolation, which is why this improvement was delayed.

---

##  How to Run and Test

### 1. Requirements and Setup (.env)
Before spinning up the containers, copy the `.env.example` file to `.env` and fill it as necessary. The application has a *Fail-Secure* policy, requiring sensitive variables to be explicit:
- `POSTGRES_PASSWORD`: Required (database password).
- `ALLOWED_ORIGINS`: List of domains for CORS (e.g., `http://localhost:3000`).
- `REDIS_URL`: Cache connection URL.
- `RATE_LIMIT_GLOBAL`: Global API request limit (default: `100/minute`).
- `RATE_LIMIT_CEP`: Request limit for CEP queries (default: `30/minute`).
- `RATE_LIMIT_OPTIONS`: Limit for CORS preflight (OPTIONS) per IP (default: `300/minute`).

### 2. Spinning Up the Infrastructure (Docker)

**For Development (Local):**
On your local machine (where you need to spin up the embedded database and cache), run the project enabling the **dev profile**:
```bash
docker-compose --profile dev up -d --build
```
This will spin up PostgreSQL (`db`) on port 5436, Redis (`cache`) operating 100% internally on the Docker network, the production FastAPI API (`api`) using Gunicorn, and the Synchronization Job (`sync_job`).

**For Production:**
The database and cache containers are isolated in the `dev` profile. If you are going to run in production and already have these services hosted on another server, provide the credentials via `.env` and run without the profile:
```bash
export POSTGRES_HOST=meu-banco-producao.com
export POSTGRES_USER=meu-usuario
export POSTGRES_PASSWORD=minha-senha
docker-compose up -d --build
```
In this scenario, only the `api` and `sync_job` will be initialized.

### 3. Automatic Synchronization (Cron Job)
The `docker-compose` itself manages the lifecycle of a *container* named `sync_job`.
When running, it will automatically invoke the `cli/scheduler.py` script in the background. It will perform the first IBGE synchronization immediately and then sleep silently for 30 days.

If for any reason you want to force a manual synchronization:
```bash
docker exec localidade_api python cli/sincronizar_dados.py
```

### 4. System Management (API Keys)
The project uses a **Zero-Trust** philosophy.
Anonymous systems (without a key) are summarily **blocked** (HTTP 401) by the Middleware. Any consumer system **must** possess a valid credential. Authenticated systems get an isolated rate limit pool.

To create a high-entropy key for a new client (run on the server):
```bash
# On Linux/Mac (Bash):
./api_key.sh criar --nome="meu_frontend"

# On Windows (CMD/PowerShell):
api_key.bat criar --nome="meu_frontend"
```

*The console will display the `X-API-Key` only once. The database stores only the SHA-256 Hash of the key.*

To revoke access (keeping the auditing history and invalidating the cache in real-time):
```bash
# On Linux/Mac (Bash):
./api_key.sh revogar --nome="meu_frontend"

# On Windows (CMD/PowerShell):
api_key.bat revogar --nome="meu_frontend"
```

**Usage in Swagger UI:**
Accessing the interactive documentation at `http://localhost:8000/docs`, you will see an **Authorize** button in the top right corner. By clicking it, you must fill in two fields:
- **X-System-ID**: The name of the system (e.g., "meu_frontend")
- **X-API-Key**: The key generated by the CLI.
After authorizing, you will be able to test all routes directly through the browser.

### 5. Quick Start (Usage Examples)

The API **mandatorily requires** the `X-System-ID` and `X-API-Key` headers in all data routes (except for Swagger UI). Failing to provide them will result in `401 Unauthorized`.

**Example via cURL (CEP Query with API Key):**
```bash
curl -X GET "http://localhost:8000/api/localidades/cep/01001000" \
     -H "X-System-ID: meu_frontend" \
     -H "X-API-Key: <CHAVE_GERADA_PELA_CLI>"
```

**Example via Python/Requests (List UFs with Cache):**
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

### 6. Using the API
The API will be available at `http://localhost:8000`. The interactive *Swagger UI* can be accessed at `http://localhost:8000/docs`.

For the detailed technical specification, parameters, flows, and JSON contracts (ideal for LLMs and Frontends use), see the **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)** file.

#### Main Endpoints:

**Query CEP:**
- `GET /api/localidades/cep/{cep}`
- **Required Headers:** `X-System-ID` (e.g., "nome_do_meu_sistema") and `X-API-Key`
- **Return Example:**
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

**Query States (UFs):**
- `GET /api/localidades/ufs`
- **Return Example (Array of Objects):**
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

**Query States (UFs) by Region:**
- `GET /api/localidades/ufs/regiao/{regiao_sigla}`
- **Path Parameter:** `regiao_sigla` (e.g., "NE", "SE", "S")

**Query Entities by IBGE ID (Natural Key):**
- All entities support querying by the exact IBGE code:
- `GET /api/localidades/municipios/codigo/{codigo_ibge}`
- `GET /api/localidades/ufs/codigo/{codigo_ibge}`

**Tolerant Textual Search (Fuzzy Search):**
- All entities have an endpoint for querying with incomplete or "dirty" names (*Case-Insensitive*):
- `GET /api/localidades/municipios/nome/{nome}` (Returns an Array)
- `GET /api/localidades/ufs/nome/{nome}`

**Batch Validation:**
- Simultaneous and optimized validation of multiple IBGE codes for batch persistence:
- `POST /api/localidades/validate-batch`

**Query All Municipalities:**
- `GET /api/localidades/municipios`

**Query Municipalities of a State:**
- `GET /api/localidades/municipios/{uf_sigla}`
- **Path Parameter:** `uf_sigla` (e.g., "SP", "RJ", "MG")
- **Return Example (Array of Objects):**
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

**Query Municipalities by Region:**
- `GET /api/localidades/municipios/regiao/{regiao_sigla}`
- **Path Parameter:** `regiao_sigla` (e.g., "NE", "SE", "S")

---
*Project idealized and developed as a georeferenced location base service.*
