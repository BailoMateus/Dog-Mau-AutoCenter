# Como Adicionar um Campo Novo na Tabela `usuario`

> Guia de referencia para a **Prova de Autoria**: adicionar um campo na tabela `usuario`,
> coletar o valor no formulario de **cadastro**, e mostrar o resultado no **painel admin de usuarios**.
>
> Este e o caminho que descobrimos ser o mais simples no projeto. Funciona para qualquer um
> dos cinco tipos de campo da prova: `INT`, `TEXT`, `FLOAT`, `VARCHAR(50)`, `DATE`.

---

## TL;DR — voce vai mexer em 8 arquivos

| # | Arquivo | O que muda | Tipo da mudanca |
|---|---|---|---|
| 1 | `infra/database/migration_add_<campo>.sql` (**novo**) | `ALTER TABLE usuario ADD COLUMN ...` | SQL |
| 2 | `infra/database/tables.sql` | Adicionar a coluna no `CREATE TABLE usuario` (linhas 2-12) | SQL |
| 3 | `backend/app/models/entities.py` | Adicionar atributo na dataclass `User` | Python |
| 4 | `backend/app/schemas/user_schema.py` | Adicionar campo em `UserCreate` (e opcionalmente `UserUpdate`/`UserPublic`) | Python |
| 5 | `backend/app/controllers/auth_controller.py` | Receber novo `Form(...)` em `register_user()` e repassar | Python |
| 6 | `backend/app/services/user_service.py` | Passar o campo do `UserCreate` para a entidade `User` | Python |
| 7 | `backend/app/repositories/user_repository.py` | Incluir o campo nas queries `INSERT` e `SELECT` | SQL/Python |
| 8 | `backend/app/templates/pages/cadastro.html` | Adicionar `<input>` no formulario | HTML |
| 9 | `backend/app/templates/partials/UserPanel.html` | Adicionar coluna `<th>` + celula `<td>` na tabela | HTML |

> Os arquivos `docker-compose.yml`, `cloudbuild.yaml`, `dockerfile`, JS do frontend, `.env.example`
> e `main.py` **nao precisam ser tocados**.

---

## Mapa do fluxo

```
NAVEGADOR                BACKEND                                    BANCO
─────────                ───────                                    ─────
[cadastro.html]
  <form action=          [auth_controller.py]
  "/auth/register">  ──> register_user(... novo: str = Form(...))
                              │
                              v
                         UserCreate(... novo=...)
                              │
                              v
                         [user_service.py]
                         create_user(data) -> User(... novo=...)
                              │
                              v
                         [user_repository.py]
                         INSERT INTO usuario (..., novo)  ─────────> tabela usuario
                                                                    (campo novo gravado)

[/admin/usuarios]
                         [user_service.py / page_controller]
                         list_users() ──> [user_repository.py]
                                          SELECT ..., novo
                                          FROM usuario               <──── le do banco
                              │
                              v
                         lista de User (dataclass)
                              │
                              v
                         [UserPanel.html]
                         {% for u in usuarios %}
                            <td>{{ u.novo }}</td>      ──> exibido na tabela
```

---

## Tipos de campo da prova — tabela de referencia

Use esta tabela para escolher os snippets corretos conforme o numero do integrante:

| Integrante | Tipo no banco | Atributo Python | Pydantic | HTML `<input>` |
|---|---|---|---|---|
| **1 (INT)** — numero da sorte | `INTEGER` | `numero_sorte: Optional[int] = None` | `numero_sorte: int \| None = None` | `<input type="number" name="numero_sorte">` |
| **2 (TEXT)** — cor favorita | `TEXT` | `cor_favorita: str = ""` | `cor_favorita: str \| None = None` | `<input type="text" name="cor_favorita">` |
| **3 (FLOAT)** — passagem onibus | `NUMERIC(10,2)` | `valor_passagem: Optional[float] = None` | `valor_passagem: float \| None = None` | `<input type="number" step="0.01" name="valor_passagem">` |
| **4 (VARCHAR 50)** — nome da mae | `VARCHAR(50)` | `nome_mae: str = ""` | `nome_mae: str \| None = Field(None, max_length=50)` | `<input type="text" name="nome_mae" maxlength="50">` |
| **5 (DATE)** — valor bolsa | `NUMERIC(10,2)` (a prova fala FLOAT) | `valor_bolsa: Optional[float] = None` | `valor_bolsa: float \| None = None` | `<input type="number" step="0.01" name="valor_bolsa">` |

> **Observacao para o Integrante 5**: o enunciado fala "campo data (FLOAT) para incluir o valor da bolsa universitaria". A descricao
> esta inconsistente (data nao combina com float). Se for **valor** mesmo, use `NUMERIC(10,2)` como float. Se for **data**, use
> `DATE` no banco e `Optional[date]` em Python (mesmo padrao do `data_nascimento` que ja existe).

---

## Receita passo-a-passo (exemplo com Integrante 1 — `numero_sorte INT`)

Substitua `numero_sorte` pelo nome do seu campo nos snippets.

### Passo 1 — Criar a migration SQL

Crie `infra/database/migration_add_numero_sorte.sql`:

```sql
-- Adiciona campo numero_sorte para a Prova de Autoria.
-- Idempotente: pode rodar varias vezes sem quebrar.
ALTER TABLE usuario
    ADD COLUMN IF NOT EXISTS numero_sorte INTEGER;
```

### Passo 2 — Atualizar `tables.sql` (consistencia)

Em [infra/database/tables.sql](infra/database/tables.sql), adicione a coluna dentro do `CREATE TABLE usuario` (logo apos `data_nascimento`):

```sql
CREATE TABLE usuario (
    id_usuario INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    ...
    deleted_at TIMESTAMP WITH TIME ZONE,
    numero_sorte INTEGER     -- <<< ADICIONADO
);
```

### Passo 3 — Registrar a migration no `docker-compose.yml`

Em [docker-compose.yml](docker-compose.yml), adicione uma linha no bloco `volumes:` apos `03_seed_admin.sql`:

```yaml
- ./infra/database/migration_add_numero_sorte.sql:/docker-entrypoint-initdb.d/04_numero_sorte.sql:ro
```

### Passo 4 — Atualizar a entidade Python

Em [backend/app/models/entities.py](backend/app/models/entities.py), dataclass `User` (linhas 9-22), adicione:

```python
@dataclass
class User:
    id_usuario: Optional[int] = None
    nome: str = ""
    ...
    deleted_at: Optional[datetime] = None
    numero_sorte: Optional[int] = None    # <<< ADICIONADO
```

E em `user_to_dict()` (linha 353), inclua a chave:

```python
return {
    ...
    'deleted_at': user.deleted_at,
    'numero_sorte': user.numero_sorte,    # <<< ADICIONADO
}
```

### Passo 5 — Atualizar o schema Pydantic

Em [backend/app/schemas/user_schema.py](backend/app/schemas/user_schema.py), classe `UserCreate` (linhas 7-16):

```python
class UserCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    ...
    data_nascimento: date | None = Field(None)
    foto_perfil: str | None = None
    numero_sorte: int | None = None    # <<< ADICIONADO
```

### Passo 6 — Receber o campo no controller de cadastro

Em [backend/app/controllers/auth_controller.py](backend/app/controllers/auth_controller.py), funcao `register_user()` (linhas 65-80), adicione um parametro `Form(...)`:

```python
@router.post("/register")
def register_user(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    cpf_cnpj: str = Form(""),
    data_nascimento: str = Form(""),
    telefone: str = Form(""),
    cep: str = Form(""),
    logradouro: str = Form(""),
    numero: str = Form(""),
    bairro: str = Form(""),
    cidade: str = Form(""),
    estado: str = Form(""),
    numero_sorte: str = Form(""),    # <<< ADICIONADO (Form sempre vem como str)
):
```

E na hora de montar `UserCreate(...)` (linhas 93-102), converta e passe:

```python
user_data = UserCreate(
    nome=nome,
    email=email,
    password=password,
    role=CLIENTE,
    ativo=True,
    telefone=telefone or None,
    cpf_cnpj=cpf_cnpj or None,
    data_nascimento=parsed_date,
    numero_sorte=int(numero_sorte) if numero_sorte else None,    # <<< ADICIONADO
)
```

> **Dica por tipo**:
> - INT: `int(numero_sorte) if numero_sorte else None`
> - FLOAT: `float(valor_passagem) if valor_passagem else None`
> - TEXT/VARCHAR: `cor_favorita or None`
> - DATE: ja tem o padrao do `data_nascimento` (use `date_type.fromisoformat()`)

### Passo 7 — Persistir no service

Em [backend/app/services/user_service.py](backend/app/services/user_service.py), funcao `create_user()` (linhas 22-32), passe o campo para a entidade:

```python
user = User(
    nome=data.nome,
    email=data.email,
    senha_hash=hash_password(data.password.strip()),
    role=data.role,
    ativo=data.ativo,
    telefone=data.telefone,
    cpf_cnpj=data.cpf_cnpj,
    data_nascimento=data.data_nascimento,
    numero_sorte=data.numero_sorte,    # <<< ADICIONADO
)
```

### Passo 8 — Atualizar as queries no repository

Em [backend/app/repositories/user_repository.py](backend/app/repositories/user_repository.py):

**8a) `create_user()` (linhas 36-50)** — INSERT:

```python
def create_user(user: User):
    query = """
    INSERT INTO usuario (nome, email, senha_hash, role, ativo, telefone, cpf_cnpj, data_nascimento, numero_sorte)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id_usuario
    """
    params = (
        user.nome, user.email, user.senha_hash, user.role,
        user.ativo, user.telefone, user.cpf_cnpj, user.data_nascimento,
        user.numero_sorte,    # <<< ADICIONADO
    )
    ...
```

**8b) `get_all_users()`, `get_user_by_id()`, `get_user_by_email()` etc** — em **TODAS** as querys `SELECT` (linhas 12-17, 25-30, 54-60, 99-104, 112-118):

```python
query = """
SELECT id_usuario, nome, email, senha_hash, role, ativo, telefone, cpf_cnpj,
       data_nascimento, created_at, updated_at, deleted_at,
       numero_sorte                    -- <<< ADICIONADO
FROM usuario
WHERE deleted_at IS NULL
ORDER BY created_at DESC
"""
```

> **Por que TODAS as SELECTs?** Porque `dict_to_user()` em [entities.py:226-230](backend/app/models/entities.py#L226-L230)
> faz `User(**data)`. Se o dict tiver chaves a mais que o dataclass nao conhece (ou faltar), ele quebra.
> Mantenha as 5 selects identicas em colunas.

### Passo 9 — Adicionar o `<input>` no formulario de cadastro

Em [backend/app/templates/pages/cadastro.html](backend/app/templates/pages/cadastro.html), entre dois `form-floating` (por exemplo, apos a data de nascimento na linha 68):

```html
<div class="form-floating mt-2">
  <input type="number" class="form-control" id="floatingSorte" name="numero_sorte" placeholder="Numero da sorte" />
  <label for="floatingSorte">Numero da sorte</label>
</div>
```

**O `name="numero_sorte"` precisa bater EXATAMENTE com o parametro `Form(...)` do controller.**

### Passo 10 — Exibir no painel admin

Em [backend/app/templates/partials/UserPanel.html](backend/app/templates/partials/UserPanel.html):

**10a) Cabecalho** (apos `<th>Status</th>` na linha 32):

```html
<th class="py-3">Numero da Sorte</th>
```

**10b) Celula** (dentro do `{% for u in usuarios %}`, apos a celula de status na linha 53):

```html
<td>{{ u.numero_sorte if u.numero_sorte is not none else '—' }}</td>
```

**10c) `colspan` da mensagem "Nenhum usuario"** (linha 74) — aumentar em 1:

```html
<td colspan="{% if user.role == 'admin' %}7{% else %}6{% endif %}" class="text-center py-4 text-muted">
```

---

## Testar tudo localmente

### 1. Resetar o banco (necessario porque o init script novo so roda em volume vazio)

```powershell
docker compose down -v
docker compose up -d
```

### 2. Confirmar que a coluna esta no banco

```powershell
docker exec -it dogmau-postgres-local psql -U dogmau -d dogmau_local -c "\d usuario"
```

Voce deve ver `numero_sorte | integer` na lista de colunas.

### 3. Subir o backend (no terminal do `backend/` com venv ativo)

```powershell
$env:PYTHONPATH = (Get-Location).Path
python app/main.py
```

### 4. Cadastrar pelo navegador

Acesse <http://localhost:8080/cadastro>, preencha o formulario (incluindo o numero da sorte) e submeta.

### 5. Conferir no banco

```powershell
docker exec -it dogmau-postgres-local psql -U dogmau -d dogmau_local -c "SELECT id_usuario, nome, email, numero_sorte FROM usuario;"
```

O admin (registro antigo) aparece com `numero_sorte = NULL` (como manda o requisito 4 da prova).
O usuario novo aparece com o valor que voce digitou.

### 6. Conferir no painel admin

1. Faca login como admin: `admin@dogmau.com` / `Senha123`.
2. Va para a area de gerenciamento de usuarios (provavelmente `/admin/usuarios` ou aba "Usuarios" no painel).
3. A nova coluna "Numero da Sorte" deve aparecer, com `—` nos registros antigos e o valor digitado no usuario recem cadastrado.

---

## Lista de verificacao (checklist da prova)

Antes de entregar, confira:

- [ ] **Requisito 1** — campo novo existe no `\d usuario` do psql.
- [ ] **Requisito 2 (FRONT/INSERT)** — `<input>` aparece no `/cadastro` e o nome do `name=` bate com o backend.
- [ ] **Requisito 2 (FRONT/SELECT)** — coluna nova aparece no painel admin (`UserPanel.html`).
- [ ] **Requisito 3 (BACK/INSERT)** — apos cadastrar via navegador, o valor aparece no banco (query psql).
- [ ] **Requisito 3 (BACK/SELECT)** — apos cadastrar, o valor aparece no painel admin.
- [ ] **Requisito 4** — registros antigos mostram `NULL` no banco e algum placeholder (ex: `—`) no painel.
- [ ] **Sem regressao** — o cadastro completo ainda funciona sem o campo novo (deixe-o opcional).

---

## Erros comuns e como diagnosticar

| Sintoma | Causa provavel | Solucao |
|---|---|---|
| Erro 422 ao cadastrar | `name` do `<input>` nao bate com o `Form(...)` do controller | Confira que ambos sao `numero_sorte` (mesma grafia) |
| `column "numero_sorte" does not exist` | Migration nao rodou | `docker compose down -v && docker compose up -d` (apaga dados!) |
| Coluna no banco mas vazia (`NULL`) mesmo no usuario novo | Esqueceu de passar `numero_sorte=...` em algum dos passos 6, 7 ou 8a | Releia a "cadeia" Controller -> Service -> Repository |
| Coluna no banco e populada, mas nao aparece no painel | Esqueceu de incluir a coluna em `get_all_users()` (passo 8b) | Adicione `numero_sorte` no `SELECT` |
| `TypeError: User.__init__() got an unexpected keyword 'numero_sorte'` | Esqueceu de adicionar o atributo na dataclass User | Passo 4 |
| Banco sobe mas init script novo nao roda | Volume `dogmau_pgdata` ja existia (init scripts so rodam no primeiro boot) | `docker compose down -v` |

---

## Por que esse caminho (cadastro + painel admin) e o mais simples

1. **O fluxo de cadastro ja existe e funciona** ponta a ponta — voce so adiciona um campo.
2. **O cadastro e form-urlencoded simples (SSR)** — nao precisa mexer em JavaScript do frontend.
3. **O painel admin (`UserPanel.html`) ja itera com `{% for u in usuarios %}`** — adicionar uma coluna e 2 linhas de Jinja.
4. **A tabela `usuario` ja tem padrao de campos opcionais** (`telefone`, `cpf_cnpj`, `data_nascimento`) — voce so segue o mesmo padrao.
5. **O backend faz CRUD sem ORM**, com queries SQL escritas a mao — fica MUITO claro onde adicionar o campo nas queries.

---

## Resumo: copie e cole essas 9 mudancas

Para cada novo campo `<CAMPO>` do tipo `<TIPO_SQL>` / `<TIPO_PY>`:

1. `infra/database/migration_add_<CAMPO>.sql` — `ALTER TABLE usuario ADD COLUMN IF NOT EXISTS <CAMPO> <TIPO_SQL>;`
2. `infra/database/tables.sql` — adicionar `<CAMPO> <TIPO_SQL>` no `CREATE TABLE usuario`
3. `docker-compose.yml` — montar a migration como `0N_<campo>.sql`
4. `entities.py` (User) — adicionar `<CAMPO>: Optional[<TIPO_PY>] = None`
5. `user_schema.py` (UserCreate) — adicionar `<CAMPO>: <TIPO_PY> | None = None`
6. `auth_controller.py` (`register_user`) — adicionar `<CAMPO>: str = Form("")` e converter ao passar para `UserCreate`
7. `user_service.py` (`create_user`) — passar `<CAMPO>=data.<CAMPO>` na construcao de `User(...)`
8. `user_repository.py` — incluir `<CAMPO>` nas queries INSERT e SELECT (todas)
9. `cadastro.html` e `UserPanel.html` — adicionar `<input>` no form e coluna na tabela

**Tempo estimado:** 30-45 minutos por campo, ja contando teste no navegador.
