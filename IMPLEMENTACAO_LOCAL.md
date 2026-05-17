# Implementacao do Ambiente Local — Guia Tecnico

> Documento de referencia para o mantenedor da branch `branch-apresentacao`.
> Para o passo-a-passo de "como rodar", veja [COMO_RODAR_LOCAL.md](COMO_RODAR_LOCAL.md).

---

## 1. Por que esta branch existe

O projeto **Dog-Mau-AutoCenter** foi desenhado para produzir em GCP:
- Backend FastAPI no **Cloud Run** ([backend/cloudbuild.yaml](backend/cloudbuild.yaml))
- Banco PostgreSQL no **Cloud SQL** (via `instance_connection_name`)
- Autenticacao social via **Firebase Auth** ([backend/firebase.json](backend/firebase.json))
- Hosting estatico via **Firebase Hosting**

O README original orienta os devs a conectarem direto no Cloud SQL remoto durante o desenvolvimento. Isso gera 3 problemas:

1. **Conflito de dados** — todo mundo escrevendo no mesmo banco compartilhado.
2. **Risco de quebrar producao** — qualquer migration ad-hoc afeta o ambiente publico.
3. **Bloqueio sem credencial** — quem nao tem acesso ao GCP nao consegue rodar nada.

A branch `branch-apresentacao` resolve isso provendo **um ambiente 100% local, isolado e descartavel** que cada integrante pode subir com 1 comando.

---

## 2. Decisoes arquiteturais (o que NAO foi mexido)

Esta foi a descoberta-chave da analise: o codigo do backend **ja suporta nativamente** o modo local. Quase nenhuma alteracao de codigo foi necessaria. Trade-offs assumidos:

| Item | Decisao | Justificativa |
|---|---|---|
| Codigo Python | **1 linha alterada** ([db.py:53](backend/app/database/db.py#L53)) | Adicionado `client_encoding="utf-8"` ao `psycopg2.connect`. Necessario em Windows pt-BR para evitar `UnicodeDecodeError` quando o Postgres devolve mensagens em latin1. Inerte em producao (Cloud Run/Cloud SQL ja sao UTF-8). |
| Frontend (Jinja/JS) | **Nao alterado** | URLs em `fetch()` ja sao relativas (`/auth/login`, `/api/users`), entao funcionam em qualquer host. |
| `dockerfile`, `cloudbuild.yaml`, `firebase.json` | **Nao alterados** | Producao continua funcionando exatamente como antes. |
| `.gitignore` | **Nao alterado** | Ja protege `.env` e `*.json` (Firebase credentials). |
| Firebase em local | **Desabilitado** | [backend/app/core/firebase.py:24-25](backend/app/core/firebase.py#L24-L25) ja eh tolerante: faz `try/except` e segue sem o JSON. Login email/senha funciona; Google Login fica OFF (aceitavel — ver secao 6). |
| Migrations SQL | **Nao alteradas** | Os 3 arquivos em [infra/database/](infra/database/) sao reaproveitados no Docker via mount com prefixo numerico. Sem duplicacao de conteudo. |
| Schema do banco | **Identico ao producao** | Mesmo `tables.sql`, mesmas migrations. Garante paridade. |

---

## 3. O que foi adicionado

Cinco arquivos novos, **zero alteracao em codigo de aplicacao**:

| Arquivo | Funcao |
|---|---|
| [docker-compose.yml](docker-compose.yml) | Sobe Postgres 16 com schema + seed automaticos |
| [backend/.env.example](backend/.env.example) | Template de variaveis ja preenchido com valores locais |
| [infra/database/seed_admin.sql](infra/database/seed_admin.sql) | Cria o usuario admin inicial (`admin@dogmau.com` / `Senha123`) |
| [IMPLEMENTACAO_LOCAL.md](IMPLEMENTACAO_LOCAL.md) | Este documento |
| [COMO_RODAR_LOCAL.md](COMO_RODAR_LOCAL.md) | Tutorial passo-a-passo para o time |

### 3.1. Como o docker-compose orquestra o schema

O Postgres oficial executa **tudo dentro de `/docker-entrypoint-initdb.d/`** em ordem alfabetica no primeiro boot (quando o volume esta vazio). Em vez de duplicar os SQLs existentes, fazemos **mount remapeado**:

```yaml
volumes:
  - ./infra/database/tables.sql:/docker-entrypoint-initdb.d/01_tables.sql:ro
  - ./infra/database/migration_add_user_fields.sql:/docker-entrypoint-initdb.d/02_add_user_fields.sql:ro
  - ./infra/database/seed_admin.sql:/docker-entrypoint-initdb.d/03_seed_admin.sql:ro
```

O prefixo `01_`, `02_`, `03_` forca a ordem correta sem renomear nada no repo.

### 3.1.1. Por que `migration_unified_users.sql` NAO eh montada

[infra/database/migration_unified_users.sql](infra/database/migration_unified_users.sql) **existe no repo mas nao eh executada pelo docker-compose**. Razoes:

1. **Eh uma migracao de DADOS, nao de schema.** Faz `INSERT INTO usuario SELECT ... FROM cliente` para mover registros antigos das tabelas `cliente`/`mecanico` para a `usuario` unificada.
2. **Em banco LOCAL/NOVO, as tabelas `cliente` e `mecanico` estao vazias** — entao a migration nao tem dados para mover. Inutil.
3. **Ela contem um bug pre-existente**: referencia `cliente.ativo` (linha 50) mas [tables.sql:15-25](infra/database/tables.sql#L15-L25) nao tem coluna `ativo` na tabela `cliente`. Em producao a migration provavelmente rodou contra um schema mais antigo, mas no atual ela aborta com:
   ```
   ERROR: column "ativo" cannot be referenced from this part of the query
   ```
4. **Quando o script falha**, o init aborta antes do `seed_admin.sql`, e o usuario admin **nao eh criado** — login impossivel.

**Decisao**: nao montar `03_unified_users.sql` no compose. Validado na pratica: com a montagem, banco subia sem o admin; sem a montagem, sobe com schema completo + admin operacional.

**Producao nao eh afetada**: a migration permanece versionada no repo para historico. Cloud SQL ja a aplicou no passado.

### 3.2. Como o seed do admin foi gerado

O hash bcrypt em [infra/database/seed_admin.sql](infra/database/seed_admin.sql) foi gerado localmente com o mesmo algoritmo que o backend usa (`passlib.context.CryptContext(["bcrypt"])`):

```bash
python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('Senha123'))"
```

A senha em texto-claro `Senha123` **so existe nesta documentacao e no .env de exemplo** — o banco guarda somente o hash.

---

## 4. Como esta branch convive com `main` (producao)

**Risco potencial**: ao mergear `branch-apresentacao` em `main`, os 5 arquivos novos viajam junto. Isso quebra producao?

**Resposta: nao.** Cada arquivo foi pensado para ser inerte em producao:

| Arquivo | Comportamento em producao |
|---|---|
| `docker-compose.yml` | Cloud Build nao executa docker-compose — ele faz `docker build ./backend`. Arquivo eh ignorado. |
| `backend/.env.example` | Pydantic Settings le **apenas** `.env` (nao `.env.example`). Cloud Run injeta vars via console/Secret Manager. Inerte. |
| `infra/database/seed_admin.sql` | So roda dentro do container Postgres do docker-compose. Cloud SQL nunca le esse arquivo. Inerte. |
| `IMPLEMENTACAO_LOCAL.md`, `COMO_RODAR_LOCAL.md` | Documentacao pura. Inerte. |
| `backend/app/database/db.py` (1 linha) | `client_encoding="utf-8"` no `psycopg2.connect`. Em Cloud SQL o cliente ja eh UTF-8 — o parametro apenas reforca o que ja era padrao. Sem alteracao de comportamento em producao. |

> **IMPORTANTE**: nao confunda com o `cloudbuild.yaml`, `firebase.json` e `dockerfile` — esses **NAO foram tocados** e continuam dirigindo o deploy.

### 4. Por que `client_encoding="utf-8"` foi adicionado ao [db.py:53](backend/app/database/db.py#L53)

Durante a validacao em Windows pt-BR, ao tentar `psycopg2.connect()` com credenciais erradas (cenario que aconteceria sempre que alguem digitasse senha errada ou caisse no Postgres nativo da maquina), o erro REAL do servidor:

```
FATAL: autenticação do tipo senha falhou para o usuário "dogmau"
```

vinha codificado em `latin1` (porque `lc_messages` do Postgres usa o locale do sistema), e o `psycopg2` tentava decodificar tudo como UTF-8 por padrao, gerando:

```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe7 in position 78
```

Esse erro **mascarava** a mensagem real (senha incorreta, banco inexistente, etc.) e tornava muito mais dificil diagnosticar problemas. Forcar `client_encoding="utf-8"` faz o Postgres ja entregar mensagens em UTF-8, alinhando com o que o `psycopg2` espera.

**Por que mantive em vez de um `os.environ["PGCLIENTENCODING"]`**: Pydantic Settings com `extra="ignore"` nao exporta variaveis nao-mapeadas para `os.environ`, entao um `PGCLIENTENCODING` no `.env` seria silenciosamente ignorado. A linha no `connect()` eh a forma minima e robusta.

---

## 5. Pontos de manutencao futura

### 5.1. Adicionei uma nova migration SQL — e agora?

Toda vez que voce adicionar um arquivo novo em [infra/database/](infra/database/) que precise rodar no setup local, **adicione 1 linha em [docker-compose.yml](docker-compose.yml)** com o proximo numero (apos o `03_seed_admin.sql`):

```yaml
- ./infra/database/migration_xyz.sql:/docker-entrypoint-initdb.d/04_xyz.sql:ro
```

E avise o time: para aplicar a nova migration, **eles precisam resetar o banco**: `docker compose down -v && docker compose up -d`.

> **Regra de ouro**: migrations de **schema** (CREATE/ALTER de tabela) sao seguras de montar. Migrations de **dados** (INSERT/UPDATE em massa) geralmente sao one-time e nao devem ser montadas — veja secao 3.1.1.

### 5.2. Mudou o schema da tabela `usuario`?

Se voce alterar colunas obrigatorias em `usuario` (ou tabelas relacionadas), atualize [infra/database/seed_admin.sql](infra/database/seed_admin.sql) para refletir a nova estrutura, senao o seed quebra no boot.

### 5.3. Mudou a senha do admin local?

Regere o hash:

```bash
python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('NovaSenha'))"
```

Substitua o hash no `seed_admin.sql` e atualize a documentacao.

---

## 6. Trade-offs assumidos (e como reverter cada um)

### 6.1. Google Login nao funciona localmente

**Por que**: `firebase-credentials.json` nao e versionado (esta no .gitignore como `*.json` e tambem explicito) e cada dev teria que baixar do console Firebase.

**Quando reverter**: se o fluxo Google for parte da apresentacao/avaliacao.

**Como reverter**: o dev baixa o `firebase-credentials.json` do console Firebase (`Project Settings > Service Accounts > Generate new private key`), coloca em `backend/firebase-credentials.json` e preenche `FIREBASE_WEB_API_KEY` no `.env`. Nada mais precisa mudar — [backend/app/core/firebase.py](backend/app/core/firebase.py) ja detecta automaticamente.

### 6.2. Cada dev tem seu proprio banco isolado

**Por que**: o objetivo da branch e justamente nao compartilhar estado.

**Implicacao**: dados de teste criados na maquina de um dev nao aparecem para os outros.

**Como reverter**: bastaria apontar `INSTANCE_CONNECTION_NAME` para o Cloud SQL — mas isso reintroduz o problema que esta branch resolve.

### 6.3. Reset de banco eh destrutivo

`docker compose down -v` apaga **todo o conteudo do banco local**. Nao tem desfazer.

**Mitigacao**: documentado claramente no [COMO_RODAR_LOCAL.md](COMO_RODAR_LOCAL.md). Se algum dev precisar preservar dados de teste, basta usar `docker compose down` (sem `-v`).

---

## 7. Checklist de validacao — TODOS OS ITENS VALIDADOS

Apos qualquer alteracao em arquivos desta branch, rode esta sequencia em uma maquina limpa para garantir que o setup funciona. Itens marcados com [x] foram validados em **2026-05-17** na maquina de desenvolvimento (Windows 11, Hyper-V backend, Postgres-18 nativo presente):

- [x] `docker compose down -v` (limpa estado anterior)
- [x] `docker compose up -d` — container fica `healthy` em ~6s
- [x] `docker compose ps` mostra `dogmau-postgres-local` como `healthy` em `0.0.0.0:5433->5432/tcp`
- [x] `docker exec -it dogmau-postgres-local psql -U dogmau -d dogmau_local -c "\dt"` lista **22 tabelas**
- [x] `docker exec -it dogmau-postgres-local psql -U dogmau -d dogmau_local -c "SELECT email, role FROM usuario;"` retorna `admin@dogmau.com | admin`
- [x] `copy backend\.env.example backend\.env` cria `.env`
- [x] Dentro de `backend/`: `python -m venv venv && venv\Scripts\Activate.ps1 && pip install -r requirements.txt`
- [x] `$env:PYTHONPATH = (Get-Location).Path; python app/main.py` sobe sem erro
- [x] `GET /saude` retorna `{"message":"API Online"}`
- [x] `GET /api/status` retorna `{"message":"Dog Mau AutoCenter API - Backend","status":"Online"}`
- [x] `GET /testar-banco` retorna `{"status":"Sucesso","mensagem":"Conectado ao Cloud SQL!"}` (texto eh hardcoded, mas conexao eh local)
- [x] `GET /` renderiza a home Jinja2 com Bootstrap, carrossel e navbar
- [x] `GET /login` renderiza a pagina de login
- [x] `POST /auth/login` (form-urlencoded) com `admin@dogmau.com/Senha123` retorna `303` + `Set-Cookie: __session=<jwt>; HttpOnly; SameSite=lax`
- [x] `POST /auth/login` com senha errada retorna `401`
- [x] `GET /auth/me` sem cookie retorna `401`
- [x] `GET /auth/me` com cookie de admin retorna `{"user_id":"1","role":"admin"}`

---

## 8. Resumo arquitetural em uma linha

> **A producao mudou zero. O local virou 1 comando.**
