# Como Adicionar um Campo Novo na Tabela `usuario`

> Guia de referencia para a **Prova de Autoria**: adicionar um campo na tabela `usuario`,
> coletar o valor no formulario de **cadastro**, e mostrar o resultado no **painel admin de usuarios**.
>
> Este e o caminho que descobrimos ser o mais simples no projeto. Funciona para qualquer um
> dos cinco tipos de campo da prova: `INT`, `TEXT`, `FLOAT`, `VARCHAR(50)`, `DATE`.

> **Atualizado em 2026-05-21 apos merge da main.**
> A receita estrutural continua identica (Controller → Service → Repository → Templates),
> mas alguns numeros de linha mudaram. Os mais importantes foram atualizados abaixo;
> se o numero exato divergir em 1-3 linhas, use o nome da funcao/classe para localizar
> (ex: `class User`, `def create_user`, `<th>Status</th>`).
>
> **Tres mudancas relevantes apos o merge:**
> - O `User` dataclass ja ganhou `foto_perfil` — seu campo novo convive com ele
> - As SELECTs em `user_repository.py` ja incluem `foto_perfil` (use como modelo)
> - Existe agora `register_user_api` (`POST /api/auth/register`) alem do SSR `register_user`.
>   Para a prova (formulario HTML) so o SSR importa; veja Passo 6.

---

## TL;DR — 1 comando SQL + 7 arquivos para editar (+ 1 opcional)

| # | Onde | O que muda | Tipo da mudanca |
|---|---|---|---|
| 1 | **Banco Postgres** (via `psql`) | `ALTER TABLE usuario ADD COLUMN ...` — comando direto, sem migration file | SQL |
| 2 | `infra/database/tables.sql` *(opcional)* | Adicionar a coluna no `CREATE TABLE usuario` para sobreviver a reset | SQL |
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

### Passo 1 — Adicionar a coluna no banco (ALTER TABLE via psql)

Com o container Postgres rodando (`docker compose ps` mostra `dogmau-postgres-local` como `healthy`),
rode UM comando ALTER TABLE direto no banco:

```powershell
docker exec -it dogmau-postgres-local psql -U dogmau -d dogmau_local -c "ALTER TABLE usuario ADD COLUMN IF NOT EXISTS numero_sorte INTEGER;"
```

Confirme que a coluna foi criada:

```powershell
docker exec -it dogmau-postgres-local psql -U dogmau -d dogmau_local -c "\d usuario"
```

Voce deve ver `numero_sorte | integer` no final da lista de colunas.

> **Por que ALTER TABLE direto e nao migration file?** Mais rapido para a prova — voce
> nao precisa criar arquivo, nao precisa mexer no `docker-compose.yml`, nao precisa resetar
> o banco. O campo eh adicionado na hora, sem perder dados.
>
> **Trade-off**: se alguem rodar `docker compose down -v` para resetar o banco, o campo SOME
> (porque ele nao esta no `tables.sql` nem em nenhum init script). Para a prova isso nao
> eh problema. Se quiser persistir, veja a nota "Opcional" abaixo.

### Passo 2 — (Opcional) Atualizar `tables.sql` para sobreviver a reset do banco

**Pule este passo se voce so quer fazer a prova funcionar.** Faca este passo se voce ou
algum colega vai resetar o volume Postgres (`docker compose down -v`) e quer manter o campo.

Em [infra/database/tables.sql](infra/database/tables.sql), adicione a coluna dentro do `CREATE TABLE usuario`:

```sql
CREATE TABLE usuario (
    id_usuario INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    ...
    deleted_at TIMESTAMP WITH TIME ZONE,
    numero_sorte INTEGER     -- <<< ADICIONADO
);
```

### Passo 3 — Atualizar a entidade Python

Em [backend/app/models/entities.py](backend/app/models/entities.py), dataclass `User` (~linhas 11-25), adicione:

```python
@dataclass
class User:
    id_usuario: Optional[int] = None
    nome: str = ""
    ...
    data_nascimento: Optional[datetime] = None
    foto_perfil: Optional[str] = None         # ja existe (veio da main)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    numero_sorte: Optional[int] = None        # <<< ADICIONADO
```

E em `user_to_dict()` (~linha 437 — apos o merge a funcao mudou de posicao), inclua a chave:

```python
return {
    ...
    'foto_perfil': user.foto_perfil,
    'created_at': user.created_at,
    'updated_at': user.updated_at,
    'deleted_at': user.deleted_at,
    'numero_sorte': user.numero_sorte,        # <<< ADICIONADO
}
```

### Passo 4 — Atualizar o schema Pydantic

Em [backend/app/schemas/user_schema.py](backend/app/schemas/user_schema.py), classe `UserCreate` (~linhas 8-32 — apos o merge tem `@field_validator` e `@model_validator`):

```python
class UserCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    ...
    data_nascimento: date | None = Field(None)
    foto_perfil: str | None = None
    numero_sorte: int | None = None    # <<< ADICIONADO

    @field_validator("email")          # validators existentes continuam abaixo
    ...
```

### Passo 5 — Receber o campo no controller de cadastro

Em [backend/app/controllers/auth_controller.py](backend/app/controllers/auth_controller.py), funcao `register_user()` SSR (~linhas 66-81), adicione um parametro `Form(...)`:

> **Atencao apos o merge da main**: existem agora DUAS rotas de cadastro neste arquivo:
> - `register_user` (linha ~66) — SSR via `Form(...)`, usado pelo formulario HTML `/cadastro`. **Esta eh a que importa para a prova.**
> - `register_user_api` (linha ~245) — API JSON via `RegisterRequest`, usado por Postman/fetch.
>
> Se voce SO mexer no SSR, o cadastro pelo navegador funciona normalmente (que eh o que a prova testa).
> O `register_user_api` pode ignorar o campo novo — nao quebra nada.


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

E na hora de montar `UserCreate(...)` (~linhas 94-103), converta e passe:

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

### Passo 6 — Persistir no service

Em [backend/app/services/user_service.py](backend/app/services/user_service.py), funcao `create_user()` (~linhas 22-33), passe o campo para a entidade:

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
    foto_perfil=data.foto_perfil,      # ja existe (veio da main)
    numero_sorte=data.numero_sorte,    # <<< ADICIONADO
)
```

### Passo 7 — Atualizar as queries no repository

Em [backend/app/repositories/user_repository.py](backend/app/repositories/user_repository.py):

**7a) `create_user()` (linhas 36-50)** — INSERT:

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

**7b) `get_user_by_email`, `get_user_by_id`, `get_all_users`, `get_user_by_role`, `get_users_by_role`** — em **TODAS as 5 querys** `SELECT` (linhas ~12-17, ~25-30, ~54-60, ~99-104, ~112-118 — apos o merge a 5a query `get_users_by_role` foi adicionada):

```python
query = """
SELECT id_usuario, nome, email, senha_hash, role, ativo, telefone, cpf_cnpj,
       data_nascimento, foto_perfil, created_at, updated_at, deleted_at,
       numero_sorte                    -- <<< ADICIONADO
FROM usuario
WHERE deleted_at IS NULL
ORDER BY created_at DESC
"""
```

> **Por que TODAS as 5 SELECTs?** Porque `dict_to_user()` em entities.py faz `User(**data)`.
> Se o dict tiver chaves a mais que o dataclass nao conhece (ou faltar), ele quebra.
> Mantenha as 5 selects identicas em colunas.
>
> **Apos o merge da main, as SELECTs ja vem com `foto_perfil`** entre `data_nascimento` e
> `created_at` — siga o mesmo padrao para o seu campo novo (adicione no final, antes do `FROM`).

### Passo 8 — Adicionar o `<input>` no formulario de cadastro

Em [backend/app/templates/pages/cadastro.html](backend/app/templates/pages/cadastro.html), entre dois `form-floating` (por exemplo, apos a data de nascimento na linha 68):

```html
<div class="form-floating mt-2">
  <input type="number" class="form-control" id="floatingSorte" name="numero_sorte" placeholder="Numero da sorte" />
  <label for="floatingSorte">Numero da sorte</label>
</div>
```

**O `name="numero_sorte"` precisa bater EXATAMENTE com o parametro `Form(...)` do controller.**

### Passo 9 — Exibir no painel admin

Em [backend/app/templates/partials/UserPanel.html](backend/app/templates/partials/UserPanel.html):

**9a) Cabecalho** (apos `<th>Status</th>`, ~linha 31):

```html
<th class="py-3">Numero da Sorte</th>
```

**9b) Celula** (dentro do `{% for u in usuarios %}`, apos a celula de status — o `</td>` do status fecha ~linha 54):

```html
<td>{{ u.numero_sorte if u.numero_sorte is not none else '—' }}</td>
```

**9c) `colspan` da mensagem "Nenhum usuario"** (~linha 74) — aumentar em 1 (de 6/5 para 7/6):

```html
<td colspan="{% if user.role == 'admin' %}7{% else %}6{% endif %}" class="text-center py-4 text-muted">
```

---

## Testar tudo localmente

> Como o campo foi adicionado via `ALTER TABLE` direto no Passo 1, NAO precisa resetar o banco.
> Se voce ja tinha o backend rodando, **reinicie ele** (`Ctrl+C` e `python app/main.py` de novo)
> para que o codigo Python novo seja carregado.

### 1. Confirmar que a coluna esta no banco

```powershell
docker exec -it dogmau-postgres-local psql -U dogmau -d dogmau_local -c "\d usuario"
```

Voce deve ver `numero_sorte | integer` na lista de colunas.

### 2. Reiniciar o backend (no terminal do `backend/` com venv ativo)

```powershell
# Ctrl+C no terminal que estava rodando, depois:
$env:PYTHONPATH = (Get-Location).Path
python app/main.py
```

### 3. Cadastrar pelo navegador

Acesse <http://localhost:8080/cadastro>, preencha o formulario (incluindo o numero da sorte) e submeta.

### 4. Conferir no banco

```powershell
docker exec -it dogmau-postgres-local psql -U dogmau -d dogmau_local -c "SELECT id_usuario, nome, email, numero_sorte FROM usuario;"
```

O admin (registro antigo) aparece com `numero_sorte = NULL` (como manda o requisito 4 da prova).
O usuario novo aparece com o valor que voce digitou.

### 5. Conferir no painel admin

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
| `column "numero_sorte" does not exist` | O `ALTER TABLE` do Passo 1 nao foi executado | Rode o comando `docker exec ... ALTER TABLE ...` do Passo 1 |
| Coluna no banco mas vazia (`NULL`) mesmo no usuario novo | Esqueceu de passar `numero_sorte=...` em algum dos passos 5, 6 ou 7a | Releia a "cadeia" Controller -> Service -> Repository |
| Coluna no banco e populada, mas nao aparece no painel | Esqueceu de incluir a coluna em alguma SELECT (passo 7b) | Adicione `numero_sorte` no `SELECT` de TODAS as 5 queries |
| `TypeError: User.__init__() got an unexpected keyword 'numero_sorte'` | Esqueceu de adicionar o atributo na dataclass User | Passo 3 |
| Apos `docker compose down -v` o campo sumiu | Esperado — `ALTER TABLE` direto nao persiste reset do banco | Rode o `ALTER TABLE` do Passo 1 de novo, OU faca o Passo 2 opcional |

---

## Por que esse caminho (cadastro + painel admin) e o mais simples

1. **O fluxo de cadastro ja existe e funciona** ponta a ponta — voce so adiciona um campo.
2. **O cadastro e form-urlencoded simples (SSR)** — nao precisa mexer em JavaScript do frontend.
3. **O painel admin (`UserPanel.html`) ja itera com `{% for u in usuarios %}`** — adicionar uma coluna e 2 linhas de Jinja.
4. **A tabela `usuario` ja tem padrao de campos opcionais** (`telefone`, `cpf_cnpj`, `data_nascimento`) — voce so segue o mesmo padrao.
5. **O backend faz CRUD sem ORM**, com queries SQL escritas a mao — fica MUITO claro onde adicionar o campo nas queries.

---

## Resumo: copie e cole essas 8 mudancas

Para cada novo campo `<CAMPO>` do tipo `<TIPO_SQL>` / `<TIPO_PY>`:

1. **Banco (psql)** — `docker exec -it dogmau-postgres-local psql -U dogmau -d dogmau_local -c "ALTER TABLE usuario ADD COLUMN IF NOT EXISTS <CAMPO> <TIPO_SQL>;"`
2. `entities.py` (User) — adicionar `<CAMPO>: Optional[<TIPO_PY>] = None` no dataclass + chave no `user_to_dict()`
3. `user_schema.py` (UserCreate) — adicionar `<CAMPO>: <TIPO_PY> | None = None`
4. `auth_controller.py` (`register_user` SSR) — adicionar `<CAMPO>: str = Form("")` e converter ao passar para `UserCreate`
5. `user_service.py` (`create_user`) — passar `<CAMPO>=data.<CAMPO>` na construcao de `User(...)`
6. `user_repository.py` — incluir `<CAMPO>` nas queries INSERT e em TODAS as 5 SELECTs
7. `cadastro.html` — adicionar `<input>` no formulario (`name` precisa bater com Form do controller)
8. `UserPanel.html` — adicionar `<th>` no cabecalho + `<td>` na linha + ajustar `colspan` da mensagem vazia

> Opcional (so se for resetar o banco): adicionar `<CAMPO> <TIPO_SQL>` no `CREATE TABLE usuario` de `infra/database/tables.sql`.

**Tempo estimado:** 20-30 minutos por campo, ja contando teste no navegador.
