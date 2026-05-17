# Como Rodar o Projeto Localmente — Guia Passo a Passo

> Voce caiu aqui porque vai trabalhar na branch `branch-apresentacao` do **Dog-Mau-AutoCenter**.
> Este guia leva voce do zero ate ver a aplicacao rodando em `http://localhost:8080`.
>
> Tempo estimado: **15-20 minutos** na primeira vez.

---

## 1. Pre-requisitos

Voce precisa instalar 3 coisas. Se ja tiver, pode pular.

| Ferramenta | Por que | Link |
|---|---|---|
| **Git** | Baixar o codigo | https://git-scm.com/downloads |
| **Python 3.11** ou superior | Rodar o backend FastAPI | https://www.python.org/downloads/ |
| **Docker Desktop** | Subir o banco PostgreSQL local | https://www.docker.com/products/docker-desktop/ |

**Opcional (recomendado):**
- **DBeaver** ou **pgAdmin** — para inspecionar o banco visualmente. https://dbeaver.io/

### Verificando se esta tudo instalado

Abra o **PowerShell** (Windows) ou **Terminal** (Mac/Linux) e cole:

```powershell
git --version
python --version
docker --version
```

Se cada comando responder com uma versao, voce esta pronto. Se algum falhar, instale-o antes de continuar.

> **Windows**: se o `python --version` mostrar uma versao 2.x ou der erro, tente `py --version` ou `python3 --version`. Use o comando que funcionar nos passos abaixo.

> **Docker Desktop precisa estar ABERTO** (icone na bandeja do sistema). Sem isso, todos os comandos `docker` vao falhar.

---

## 2. Baixar o codigo

```powershell
git clone https://github.com/BailoMateus/Dog-Mau-AutoCenter.git
cd Dog-Mau-AutoCenter
git checkout branch-apresentacao
```

Voce deve ver no terminal: `Switched to branch 'branch-apresentacao'`.

---

## 3. Criar o arquivo `.env`

Este arquivo guarda configuracoes locais (senhas, conexoes). Ja existe um modelo pronto.

**Windows (PowerShell):**
```powershell
copy backend\.env.example backend\.env
```

**Mac/Linux:**
```bash
cp backend/.env.example backend/.env
```

> Voce **nao precisa editar** o `.env` — os valores ja vem prontos para o ambiente local.

---

## 4. Subir o banco de dados (PostgreSQL via Docker)

Na **raiz do projeto** (pasta `Dog-Mau-AutoCenter`), rode:

```powershell
docker compose up -d
```

Na primeira vez, o Docker vai baixar a imagem `postgres:16-alpine` (~80MB) e criar o container. Demora 30-60 segundos.

### Conferir que o banco subiu

```powershell
docker compose ps
```

Voce deve ver algo como:
```
NAME                       STATUS                   PORTS
dogmau-postgres-local      Up X seconds (healthy)   0.0.0.0:5432->5432/tcp
```

A palavra-chave eh **`healthy`**. Se aparecer `starting`, espere mais alguns segundos e rode de novo.

### O que aconteceu por baixo

No primeiro boot, o Docker executou automaticamente 4 scripts SQL (na ordem):
1. `tables.sql` — cria todas as tabelas
2. `migration_add_user_fields.sql` — adiciona campos extras
3. `migration_unified_users.sql` — unifica `cliente` + `mecanico` em `usuario`
4. `seed_admin.sql` — cria o usuario admin (`admin@dogmau.com` / `Senha123`)

---

## 5. Instalar as dependencias do Python

Entre na pasta `backend` e crie um **ambiente virtual** (isolado da sua maquina):

```powershell
cd backend
python -m venv venv
```

### Ativar o ambiente virtual

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

> Se aparecer erro de "execution policy", rode UMA vez (como admin nao necessario):
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```
> Depois tente ativar novamente.

**Mac/Linux:**
```bash
source venv/bin/activate
```

Voce deve ver `(venv)` aparecer no comeco do seu prompt do terminal.

### Instalar pacotes

```powershell
pip install -r requirements.txt
```

Demora 1-2 minutos. Ignore eventuais warnings amarelos — so erros vermelhos sao problema.

---

## 6. Rodar o backend

Ainda dentro de `backend/` e com o `venv` ativo:

**Windows (PowerShell):**
```powershell
$env:PYTHONPATH = (Get-Location).Path
python app/main.py
```

**Mac/Linux:**
```bash
export PYTHONPATH=$(pwd)
python app/main.py
```

Voce deve ver logs parecidos com:
```
INFO:     Started server process [...]
INFO:     Waiting for application startup.
[INFO] app.main: API iniciada (FastAPI) ...
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

> Um warning sobre `firebase-credentials.json` nao encontrado eh **esperado** — em ambiente local o Firebase fica desabilitado de proposito. Voce pode ignorar.

---

## 7. Testar se esta tudo funcionando

Com o backend rodando, abra **outro terminal** e rode:

```powershell
curl http://localhost:8080/saude
curl http://localhost:8080/testar-banco
```

Respostas esperadas:
- `/saude` → `{"message":"API Online"}`
- `/testar-banco` → `{"status":"Sucesso","mensagem":"Conectado ao Cloud SQL!"}` (a mensagem diz "Cloud SQL" mas voce esta conectado no Postgres local — eh so o texto da resposta)

### Abrir no navegador

Acesse: **http://localhost:8080/**

Voce deve ver a home page do site.

### Fazer login

Acesse: **http://localhost:8080/login**

Credenciais do admin local:
- **Email**: `admin@dogmau.com`
- **Senha**: `Senha123`

Apos logar, voce deve cair no painel administrativo.

> O botao **"Entrar com Google"** vai dar erro — isso eh proposital. Em ambiente local o Firebase fica desabilitado. Use sempre o login por email/senha.

---

## 8. Comandos uteis (cheatsheet)

| O que voce quer fazer | Comando |
|---|---|
| Parar o backend | `Ctrl+C` no terminal onde ele esta rodando |
| Parar o banco (preserva dados) | `docker compose down` |
| **Resetar o banco do zero** (apaga tudo) | `docker compose down -v && docker compose up -d` |
| Ver logs do banco em tempo real | `docker compose logs -f postgres` |
| Conectar no banco via terminal | `docker exec -it dogmau-postgres-local psql -U dogmau -d dogmau_local` |
| Listar tabelas no banco | (dentro do psql) `\dt` |
| Sair do psql | `\q` |
| Reativar o ambiente Python (depois de fechar o terminal) | `cd backend; .\venv\Scripts\Activate.ps1` |

### Conectar com DBeaver/pgAdmin

| Campo | Valor |
|---|---|
| Host | `localhost` |
| Porta | **`5433`** (nao 5432 — evita conflito com Postgres nativo) |
| Banco | `dogmau_local` |
| Usuario | `dogmau` |
| Senha | `dogmau` |

---

## 9. Troubleshooting

### "port is already allocated" / "Error: bind: address already in use" na 5433

A porta padrao deste projeto eh **5433** (escolhida para evitar o `5432` ocupado por Postgres nativo). Se mesmo a 5433 estiver em uso, voce tem duas opcoes:

**Opcao A — usar outra porta livre (ex: 5434):**
1. Edite [docker-compose.yml](docker-compose.yml) e troque `"5433:5432"` por `"5434:5432"`.
2. Edite `backend/.env` e ajuste `DATABASE_URL=postgresql://dogmau:dogmau@localhost:5434/dogmau_local`.
3. `docker compose down -v && docker compose up -d`.

**Opcao B — descobrir e parar o que esta usando a 5433:**
- Windows (PowerShell): `Get-NetTCPConnection -LocalPort 5433 -State Listen` → veja o `OwningProcess` e decida.
- Mac/Linux: `lsof -i :5433` ou `ss -ltnp | grep 5433`.

### Docker diz que mapeou a porta mas o backend nao conecta

Sintoma: `docker compose ps` mostra `0.0.0.0:5433->5432/tcp`, mas o backend recebe `password authentication failed`.

Causa: Docker Desktop em Hyper-V backend **falha silenciosamente no bind** quando a porta ja esta ocupada. Voce esta caindo em outro Postgres (provavelmente o `postgresql-x64-XX` nativo).

Diagnostico (Windows PowerShell):
```powershell
Get-NetTCPConnection -LocalPort 5433 -State Listen
```
Se o `OwningProcess` for `postgres.exe` em vez de `vmmem`/processo Docker, voce esta no caso acima. Use a Opcao A acima para escolher outra porta.

### `ModuleNotFoundError: No module named 'app'`

Voce esqueceu de setar `PYTHONPATH`. Volte ao **passo 6** e rode os 2 comandos juntos:

```powershell
$env:PYTHONPATH = (Get-Location).Path
python app/main.py
```

Garanta que voce esta dentro da pasta `backend/`.

### `pip install` falha em `psycopg2-binary` no Windows

Instale o **Microsoft C++ Build Tools**:
https://visualstudio.microsoft.com/visual-cpp-build-tools/

Apos instalar, rode `pip install -r requirements.txt` de novo.

### O login com `admin@dogmau.com` / `Senha123` nao funciona

1. Confirme que o banco subiu certo: `docker exec -it dogmau-postgres-local psql -U dogmau -d dogmau_local -c "SELECT email FROM usuario;"`
2. Se nao aparecer o admin, resete o banco: `docker compose down -v && docker compose up -d`. Os seeds so rodam quando o banco esta vazio.

### "Cannot connect to the Docker daemon"

O Docker Desktop nao esta aberto. Abra o app e espere o icone ficar verde/estavel antes de tentar de novo.

### Esqueci de ativar o venv e instalei pacotes na maquina inteira

Sem problema — funciona, so polui sua instalacao global. Para limpar: ativa o venv certinho e reinstala dentro dele. Os pacotes "extras" no global nao quebram nada.

### Mudou alguma migration / quero rebootar o banco

```powershell
docker compose down -v
docker compose up -d
```

O `-v` apaga o volume. Os scripts de init rodam de novo do zero. Voce volta a ter o admin inicial e nenhum outro dado.

---

## 10. Fluxo do dia-a-dia

Depois da primeira configuracao, no dia seguinte voce so precisa de **3 comandos**:

```powershell
# 1. Subir o banco (se nao estiver rodando)
docker compose up -d

# 2. Entrar no backend e ativar venv
cd backend
.\venv\Scripts\Activate.ps1

# 3. Rodar a API
$env:PYTHONPATH = (Get-Location).Path
python app/main.py
```

Para parar tudo no fim do expediente:

```powershell
# Ctrl+C no terminal da API
docker compose down   # opcional: para o banco tambem (sem -v para preservar dados)
```

---

## 11. Onde pedir ajuda

Se travar em algum ponto:
1. Releia a secao 9 (Troubleshooting).
2. Veja [IMPLEMENTACAO_LOCAL.md](IMPLEMENTACAO_LOCAL.md) para entender a arquitetura.
3. Fale com o mantenedor da branch (Mateus Bailo) com:
   - O comando exato que voce rodou
   - A mensagem de erro completa
   - Seu sistema operacional

Bom desenvolvimento.
