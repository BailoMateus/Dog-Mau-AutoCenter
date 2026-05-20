# Relatório de Análise do Backend: Dog-Mau-AutoCenter

## 1. Estrutura do Backend
O projeto implementa uma arquitetura MVC/Layers explicitamente separada, e embora utilize **FastAPI** como o "motor" do roteamento HTTP, toda a orquestração interna (banco de dados, injeções, validações) foi programada manualmente.
- **Padrão de Pastas:**
  - `controllers/`: Recebe as requisições HTTP e lida com o repasse de parâmetros ou definições de headers/cookies.
  - `services/`: Camada de regras de negócio. Onde ocorre a verificação dos dados, criação de senhas provisórias e orquestração de chamadas.
  - `repositories/`: Camada isolada que contém somente strings SQL explícitas e interação pura com o banco de dados.
  - `models/`: Ausência de classes ORM. As entidades (como `User`, `Veiculo`) são criadas como `@dataclass` puras do Python. Possuem funções utilitárias manuais (ex: `dict_to_user`, `user_to_dict`) para converter os dados do banco.
  - `database/`: Onde o acesso físico é abstraído. Há um gerenciador manual de contexto (`get_db_connection`) usando a biblioteca `psycopg2`.
  - `middlewares/`: Concentra lógicas aplicadas de forma abrangente, como extração manual de Tokens de usuários (`auth_middleware.py`).

## 2. Fluxo de Requisição
Tomando como exemplo a rota de **Login**:
1. **Entrada HTTP:** O cliente submete um formulário via `POST`.
2. **Middleware:** A request passa pelo `log_requests` (em `main.py`) que temporiza o tempo de processo.
3. **Controller (`auth_controller.py`):** Recebe os campos interceptados e os encaminha.
4. **Service (`auth_service.py`):** Tenta processar o login com os dados. Retorna falha ou sucesso (com um token recém-gerado).
5. **Repository (`user_repository.py`):** O serviço chama o repositório, que por sua vez manda um comando raw de `SELECT *` para o `db.py`.
6. **Resposta Final:** O Controller recebe o JWT criado, gera uma resposta de Redirecionamento (HTTP 303), invoca a injeção local manual do cookie via `_set_auth_cookie`, e libera a resposta de volta ao Frontend.

## 3. Sistema de Usuários e Roles
Existem 3 papéis configurados de modo determinístico no sistema: **admin**, **mecanico** e **cliente**.
- **Definição e Armazenamento:** Estão definidos como variáveis constantes no arquivo `core/roles.py`. No banco de dados, são armazenados como *strings* comuns dentro da coluna `role` da tabela `usuario`.
- **Verificações (`core/security.py`):** A proteção do sistema acontece na injeção de dependência `require_role(allowed_roles)`. Ela analisa o payload presente no JWT (que guarda o papel daquele usuário) e compara se bate com as roles liberadas para a rota. Se for inválido, o sistema aciona manualmente um erro `HTTP_403_FORBIDDEN`.

## 4. Regras de Negócio Importantes
- **Soft Delete:** A exclusão de usuários não remove o dado físico (`DELETE`). A função `soft_delete_user` injeta o timestamp na coluna `deleted_at` e inativa a boolean `ativo`.
- **Integração Auth do Google:** Quando um login social é efetuado e o e-mail não é encontrado no sistema, o backend assume o papel de gerar um usuário cliente automático, mas constrói uma senha aleatória obrigatória via `uuid.uuid4() + "A1@"` para permitir a compatibilidade com a tabela física de usuários sem quebrar constraints.
- **Acoplamento de Formulários:** Durante a operação de Cadastro de Usuário, caso as "keys" do logradouro venham preenchidas, o sistema automaticamente invoca o serviço de Endereços (`endereco_service.add_endereco_to_user`), atrelando as duas entidades na mesma chamada HTTP.

## 5. Autenticação (Foco em Cookies)
A autenticação do sistema é efetuada por via de **JSON Web Tokens (JWT) atrelados dentro de Cookies HttpOnly**.
- **Criação e Fluxo do Cookie:** Quando um usuário é autenticado em `/auth/login`, o controller chama a função interna `_set_auth_cookie`. Essa função utiliza `response.set_cookie(...)` e injeta a chave chamada `__session`.
- **Flags de Segurança:**
  - `httponly=True`: Garante que nenhum JavaScript (inclusive malicioso) no frontend consiga ler esse cookie (`document.cookie`).
  - `samesite="lax"`: Mitiga possíveis ataques CSRF (Cross-Site Request Forgery).
  - `secure=_IS_PRODUCTION`: Se o servidor estiver operando hospedado via K_SERVICE, o cookie só é liberado em ambiente HTTPS.
- **Como é Lido no Backend:** Em cada chamada protegida, o interceptor do FastAPI aciona `get_current_user` em `auth_middleware.py`. Esse interceptor lê o header de Authorization, mas se estiver ausente, ele faz um *fallback* diretamente para ler `request.cookies.get("__session")`. A validação do token é feita desencriptando com a chave manual da aplicação.
- **Logout:** A rota `/logout` limpa completamente os cookies, sobrescrevendo a resposta com `response.delete_cookie("__session")` e devolvendo o cliente para a tela inicial.

## 6. Segurança
- **Injeção SQL Bloqueada:** A arquitetura manual do repositório contorna os riscos de Injection usando parâmetros parametrizados puros (o driver Python injeta as strings de forma isolada nos "placeholders" `%s` de forma segura).
- **Firebase Auth Seguro:** O controlador que processa o login via Google não acredita unicamente no corpo JSON enviado. Ele obrigatoriamente despacha o `id_token` do Google para a biblioteca Google Cloud Admin do Firebase (Server-Side) para desencriptar, aferindo assim se aquele token social é fidedigno.

## 7. Banco de Dados
- Não há ORM (Nenhum SQLAlchemy, Prisma, etc).
- **Transações controladas via Psycopg2:** O fluxo é coordenado usando `@contextmanager` para fechar corretamente a conexão nativa com o Cloud SQL.
- **Comandos RawSQL:** O `execute_query` abre o cursor, injeta as sentenças, fecha e já retorna um dicionário de propriedades usando o `RealDictCursor`. Os mapeamentos para as classes devem ser chamados logo depois pelo programador (ex: pegando os arrays devolvidos e jogando num for-loop para converter em objetos Python).

## 8. Frontend (Visão Superficial)
- **Renderização e Arquitetura:** O Frontend também reside internamente no backend. Ele adota o modelo **SSR (Server-Side Rendering)**, o que significa que o HTML é gerado no backend pelo compilador **Jinja2** e servido no `page_controller.py`.
- **Comunicação Cliente-Servidor:** Em vez de usar scripts JavaScript densos com React / Fetch API / Axios para se autenticar e pegar JSON, o cliente age via formulários tradicionais `<form method="POST" action="/auth/login">`. O retorno final não é um JSON mas um Redirecionamento 303 informando o Browser a mudar de URL com as chaves de autorização de rede ativadas (os cookies).

## 9. Resumo Final
O sistema foge do convencional e aposta na abordagem *"Hands-On"*. Ele abdica de abstrações prontas que geram SQLs autônomos para obter um ganho gigante de clareza: o programador tem acesso integral para tunar e ler os SQLs sem precisar entender a mágica do ORM.
- **Vantagens Práticas:** Queries simples de debugar, total controle do fluxo de cookies de autenticação, e um modelo robusto para prevenção de problemas no Frontend através do modelo SSR nativo do Jinja.
- **Eventuais Desvantagens:** Crescimento rápido do "Boilerplate". Como os mapeadores (Modelos -> Dicionários de Banco de Dados) não são automatizados, os programadores podem acabar introduzindo erros lógicos de digitação em novos endpoints. Além disso, as strings SQL em Python se beneficiariam muito de testes exaustivos visto a ausência da tipagem que a camada ORM traria.
