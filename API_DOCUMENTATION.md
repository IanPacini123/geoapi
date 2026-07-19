# Documentacao da API GeoCEP

Este documento contem a especificacao tecnica detalhada de todos os endpoints da API "Alimentar Enderecos", desenvolvida com FastAPI. Foi estruturado de forma legivel para integracao por IA (LLMs) ou desenvolvedores frontend.

**URL Base:** `http://<seu-host>:8000/api/localidades`

> [!IMPORTANT]
> **Cabecalhos Globais (Headers)**
> Todas as requisicoes para a API **devem** obrigatoriamente incluir o cabecalho `X-System-ID`.
> - **Chave:** `X-System-ID`
> - **Valor:** O nome do seu sistema/microsservico (ex: "frontend-cliente", "servico-consumidor")
> - **Objetivo:** Rastreabilidade e auditoria (o middleware intercepta e registra a requisicao).
>
> [!WARNING]
> **BREAKING CHANGE (Fase 10):** A partir desta versao, a ausencia do cabecalho `X-System-ID` resultara imediatamente na rejeicao da requisicao com o status HTTP `401 Unauthorized`. O comportamento legado de assumir `"desconhecido"` foi revogado para garantir *Fail Secure*.
>
> **Acesso pelo Swagger UI (`/docs`):** O proprio site da documentacao interativa esta livre de bloqueio, permitindo que voce o acesse. Para testar as rotas por dentro dele, clique no botao **Authorize** (no topo direito) e preencha a sua dupla de credenciais (`X-System-ID` e `X-API-Key`). Apos isso, o Swagger injetara automaticamente os cabecalhos em todos os seus testes de rota.

---

## 1. Busca de CEP e Enderecamento

### Consultar um CEP

- `GET /api/localidades/cep/{cep}`
- **Headers:** 
  - `X-System-ID` (Obrigatorio): Identifica o sistema consumindo a API.
  - `X-API-Key` (Obrigatorio): Chave de autenticacao obrigatoria gerada pela CLI.

- **Path Parameter:**
  - `cep` (string): CEP contendo 8 digitos, podendo conter ou nao o traco (ex: `01310930` ou `01310-930`).
- **Respostas:**
  - `200 OK`: Retorna o objeto de CEP formatado. **Nota:** Para CEPs gerais (ex: municipios pequenos ou zonas rurais), os campos `logradouro` e `bairro` podem retornar `null`.
  - `400 Bad Request`: Caso o CEP seja invalido (diferente de 8 caracteres numericos).
  - `401 Unauthorized`: Caso os cabecalhos `X-System-ID` ou `X-API-Key` nao sejam enviados ou o hash da chave seja invalido/revogado.
  - `404 Not Found`: Caso o CEP nao exista nas bases federais e nem no cache local.
  - `429 Too Many Requests`: Limite de uso excedido (Cota estrita isolada e configuravel no `.env` via `RATE_LIMIT_CEP`, padrao de 30 requisicoes por minuto por combinacao de IP e X-System-ID neste endpoint).
**Exemplo de Resposta (200 OK):**
```json
{
  "cep": "01310930",
  "logradouro": "Avenida Paulista",
  "bairro": "Bela Vista",
  "localidade": "Sao Paulo",
  "uf": "SP",
  "uf_codigo": 35,                 // ForeignKey: Referencia ao id interno da tabela de Uf
  "municipio_codigo": 3550308,     // ForeignKey: Referencia ao id interno da tabela de Municipio
  "tipo_logradouro_codigo": 4,     // ForeignKey: Referencia ao id interno da tabela TipoLogradouro
  "data_criacao": "2026-06-26T16:44:50.167833"
}
```

---

## 2. Entidades Geograficas Basicas (IBGE)

Todas as entidades (UFs, Municipios, Paises, Regioes, etc.) possuem as seguintes mecanicas de busca e listagem integradas:
- `GET /`: Retorna a lista completa. Suporta parametros de query opcionais para paginacao: `?skip=0&limit=100`.
- `GET /codigo/{codigo_ibge}`: Busca exata pelo ID oficial numerico (Natural Key). Retorna Objeto unico ou `404`.
- `GET /nome/{nome}`: Busca parcial *Fuzzy* e *Case-Insensitive* (`ilike`). Util para sistemas legados com strings sujas. Sempre retorna um `Array` (lista). **Nota: Em caso de ausencia de correspondencia, retorna `200 OK` com um array vazio `[]` (nao retorna `404`).**

> [!NOTE]
> **Rate Limit (Protecao Contra Abusos):** Todos os endpoints do IBGE (abaixo) compartilham um limite global configuravel no `.env` via `RATE_LIMIT_GLOBAL` (padrao de `100 requisicoes por minuto`).
> - **Zero-Trust:** Sistemas anonimos ou com `X-API-Key` invalida sao **bloqueados imediatamente** com `401 Unauthorized` antes mesmo de entrarem no rate limit.
> - **Isolamento de Cota:** Todo sistema validado com `X-API-Key` valida recebe uma **cota isolada exclusiva** atrelada a identidade (`IP:Sistema`), garantindo performance blindada contra *noisy neighbors*.

### Paises (`/paises`)
- `GET /paises`: Retorna todos.
- `GET /paises/codigo/{codigo_ibge}`
- `GET /paises/nome/{nome}`

### Regioes (`/regioes`)
- `GET /regioes`: Retorna todas.
- `GET /regioes/codigo/{codigo_ibge}`
- `GET /regioes/nome/{nome}`

### Estados/UFs (`/ufs`)
- `GET /ufs`: Retorna todas.
- `GET /ufs/codigo/{codigo_ibge}`
- `GET /ufs/nome/{nome}` (Ex: `/nome/paulo` retorna `[{"nome": "Sao Paulo", ...}]`)
- `GET /ufs/regiao/{regiao_sigla}`: Filtra por regiao.

---

## 3. Estrutura Geografica Avancada (Mesorregioes e Microrregioes)

### Mesorregioes (`/mesorregioes`)
- `GET /mesorregioes`: Retorna todas (FK: `uf_id`).
- `GET /mesorregioes/codigo/{codigo_ibge}`
- `GET /mesorregioes/nome/{nome}`

### Microrregioes (`/microrregioes`)
- `GET /microrregioes`: Retorna todas (FK: `mesorregiao_id`).
- `GET /microrregioes/codigo/{codigo_ibge}`
- `GET /microrregioes/nome/{nome}`

### Regioes Intermediarias (`/regioes-intermediarias`)
- `GET /regioes-intermediarias`: Retorna todas (Classificacao 2017+).
- `GET /regioes-intermediarias/codigo/{codigo_ibge}`
- `GET /regioes-intermediarias/nome/{nome}`

### Regioes Imediatas (`/regioes-imediatas`)
- `GET /regioes-imediatas`: Retorna todas (Classificacao 2017+).
- `GET /regioes-imediatas/codigo/{codigo_ibge}`
- `GET /regioes-imediatas/nome/{nome}`

---

## 4. Municipios

### Municipios (`/municipios`)
- `GET /municipios`: Retorna todos os 5570+ municipios.
- `GET /municipios/codigo/{codigo_ibge}`
- `GET /municipios/nome/{nome}` (Atencao: Retorna um Array, pois ha municipios homonimos. Ex: `/nome/bom%20jesus` retornara 23+ municipios de estados diferentes).
- `GET /municipios/{uf_sigla}`: Retorna os municipios de uma UF especifica.
- `GET /municipios/regiao/{regiao_sigla}`: Retorna os municipios de uma macro-regiao.

---

## 5. Enderecamento e Correios

### Tipos de Logradouro (`/tipos-logradouro`)
Retorna as descricoes oficias padronizadas pelos Correios (Ex: Rua, Avenida, Praca).
- `GET /tipos-logradouro`
- `GET /tipos-logradouro/descricao/{descricao}` (Busca parcial via `.ilike()`)

---

## 6. Validacao em Lote (Batch Validation)

### Validar Multiplos Codigos IBGE (`POST /validate-batch`)
Realiza a validacao de multiplos codigos numericos (IBGE) de municipios, UFs e paises em uma unica requisicao. Desenvolvido para altissima performance usando clausulas `IN` do SQLAlchemy, mitigando o problema N+1 ao persistir formularios complexos no microsservico consumidor.

- **Corpo da Requisicao (JSON):**
```json
{
  "municipiosIbge": [3550308, 2304400],
  "ufsIbge": [35, 23],
  "paisesIbge": [76]
}
```

- **Respostas:**
  - `200 OK`: Retorna o status da validacao e os erros se houverem. Se a flag `valido` for `true`, significa que todos os IDs enviados existem no banco de dados.

**Exemplo de Resposta (Invalida):**
```json
{
  "valido": false,
  "mensagensErro": [
    "Municipio com IBGE 999999 nao encontrado.",
    "UF com IBGE 99 nao encontrada."
  ]
}
```
