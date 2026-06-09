# Changelog de Ajustes — Dog Mau Auto Center

Data: 2026-06-09

Registro das mudanças realizadas conforme a lista de ajustes solicitada. Cada seção
indica o que **já existia** e o que foi **alterado**, com os arquivos tocados.

Verificações executadas após as alterações:

- `python -m py_compile` nos arquivos Python alterados — OK
- `import app.main` (app FastAPI carrega sem erros de import) — OK
- Parse de todos os templates Jinja alterados — OK
- `node --check` nos arquivos JS standalone alterados — OK

---

## 1. Produtos e peças (fotos)

- Upload / atualização / exibição de **foto de produtos** já era funcional
  (endpoints `/api/produtos`, coluna `imagem_produto`, modal de gerenciamento e
  cards da loja).
- **Foto de peças**: o backend já existia (`/pecas`, coluna `imagem_peca`,
  `peca_service.save_peca_imagem_peca`), mas faltava interface. A funcionalidade
  de upload/atualização/exibição de foto de peças foi adicionada via a nova seção
  de gerenciamento de Peças (ver Seção 4) e via a vitrine da loja.

**Arquivos:** `backend/app/templates/partials/ProdutoPanel.html`,
`backend/app/templates/pages/loja.html` (detalhado na Seção 4).

---

## 2. Painel de Gestão

### Barra de navegação
- Removida a barra de navegação secundária (linha de botões *Relatórios /
  Movimentações Financeiras / Movimentações de Estoque*). Mantida apenas a barra
  de abas principal, que já contém todas as opções (incluindo Relatórios,
  Financeiro e Estoque).
- **Arquivo:** `backend/app/templates/pages/painel.html`.

### Aba de Pedidos
- Já estava disponível para administradores e mecânicos e já listava os itens de
  cada pedido (`order_card.html` itera `ped.itens`).
- O seletor de status e o botão de exclusão do card de pedido **não possuíam
  handler JS** (eram inertes). Foram ligados: alteração de status faz
  `PATCH /api/pedidos/{id}` e o botão de excluir abre o modal de exclusão. Assim
  admin/mecânico conseguem **aprovar/concluir** os pedidos pela aba.
- **Arquivo:** `backend/app/templates/partials/PedidoPanel.html`.

### Orçamento
- A criação automática de Ordem de Serviço a partir da **aprovação de um
  orçamento** já existia e foi mantida.
- **Arquivo (sem alteração):** `backend/app/services/orcamento_approval_service.py`.

### Ordem de Serviço
- **Correção do erro na tela de detalhes:** as consultas de serviços, peças e
  movimentações da OS apontavam para tabelas inexistentes
  (`orcamento_servico_item` / `orcamento_peca_item`) com colunas inexistentes
  (`valor_unitario`, `p.preco`). O serviço foi redirecionado para os repositórios
  corretos:
  - serviços → `os_servico_repository.get_servicos_by_os`
  - peças → `os_peca_repository.get_pecas_by_os`
  - movimentações → `movimentacao_estoque_repository.get_movimentacoes_by_os`
  Isso garante o carregamento completo das informações da OS.
- **Atribuição de OS a Mecânico ou Administrador:** o backend
  (`check_mecanico_atribuivel`) já aceitava ambos os papéis, mas o seletor só
  listava mecânicos. A query passou a incluir também administradores.
- **Arquivos:** `backend/app/services/ordem_servico_service.py`,
  `backend/app/controllers/page_controller.py`.

---

## 3. Movimentações Financeiras (automáticas)

- **Conclusão de Pedido → entrada:** já existia em `pedido_service.update_pedido`
  (ao mudar status para `concluido`). Agora é acionável pela interface graças ao
  seletor de status ligado na aba Pedidos (Seção 2).
- **Orçamento concluído → entrada (valor da OS):** já existia na conclusão da OS
  (`ordem_servico_service.concluir_ordem_servico` registra entrada = valor total
  da OS).
- **Movimentação de estoque MANUAL → saída:** adicionada. Ao registrar uma
  movimentação manual de estoque, é criada automaticamente uma movimentação
  financeira do tipo **saída** com valor = quantidade × preço unitário da peça.
  - Implementado em `movimentacao_estoque_service` (funções chamadas **somente**
    pela UI manual). Os fluxos de OS e de Pedido usam o repositório diretamente,
    portanto **não há duplicação** de lançamento.
- **"ID de Pagamento" removido da interface:** retirado o campo do formulário e a
  coluna da tabela de movimentações financeiras (ele é gerado automaticamente).
- **Arquivos:** `backend/app/services/movimentacao_estoque_service.py`,
  `backend/app/templates/pages/movimentacoes_financeiras.html`,
  `backend/static/js/movimentacoes_financeiras.js`.

---

## 4. Produtos × Peças (separação no frontend)

### Tela de Produtos (loja)
- A vitrine foi dividida em duas seções distintas: **"Produtos"** e **"Peças"**,
  sem misturar (tabelas diferentes no backend). A seção de Peças exibe a foto
  atual (`imagem_peca`), nome, preço e estoque.
- O controller da loja passou a carregar e enviar `pecas` ao template.
- **Arquivos:** `backend/app/templates/pages/loja.html`,
  `backend/app/controllers/page_controller.py`.

### Tela de Gerenciamento de Produtos e Peças
- Mantida a seção de **Produtos** (comportamento atual) e adicionada uma seção de
  **Peças** com as mesmas colunas (ID, Imagem, Nome, Descrição, Preço, Estoque,
  Ações) e CRUD completo (criar/editar/excluir) com upload de imagem via `/pecas`.
- O painel passou a carregar e enviar `pecas` ao template (admin/mecânico).
- **Arquivos:** `backend/app/templates/partials/ProdutoPanel.html`,
  `backend/app/controllers/page_controller.py`.

> Observação: a entidade `Peca` não possui campo `descricao` no banco; para manter
> as mesmas colunas, a coluna "Descrição" das peças exibe "—".

---

## 5. Timeout

- **Token com validade de 12 horas:** `access_token_expire_minutes` alterado de
  `60` para `720` no padrão das configurações e no `.env` local.
- **Logout automático após 1 hora sem atividade:** novo script que monitora
  atividade (mouse, teclado, scroll, toque, clique) e redireciona para `/logout`
  após 1h ocioso. Atua apenas quando há usuário autenticado.
- **Arquivos:** `backend/app/core/settings.py`, `backend/.env`,
  `backend/static/js/session-timeout.js` (novo),
  `backend/app/templates/base.html`.

---

## 6. Finalizar Compra (checkout)

### Seu Carrinho
- Exibe o **valor total** da compra (soma do preço de todos os itens do carrinho).
- **Sem frete** (linha de frete removida).
- Exibe somente a opção **"À retirar"**.

### Informações para Retirada
- Seção "Informações de Entrega" renomeada para **"Informações para Retirada"**.
- Removidos todos os campos de endereço.
- Campos: **Comprador** (preenchido com o usuário), **Telefone** (telefone do
  usuário) e **Forma de Pagamento**.
- Forma de Pagamento contém exclusivamente: **Cartão de Débito, Cartão de Crédito,
  Pix, Dinheiro**.

### Comportamento
- Texto do botão alterado para **"Finalizar Pedido"**.
- Ao clicar, cria automaticamente um pedido com status **"pendente"** (disponível
  para aprovação por administrador ou mecânico na aba Pedidos).
- Após a criação, o carrinho é esvaziado automaticamente.
- **Arquivos:** `backend/app/templates/pages/checkout.html`,
  `backend/static/js/checkout.js`.

---

## Arquivos alterados (resumo)

| Arquivo | Mudança |
|---|---|
| `backend/app/core/settings.py` | Token 12h (720 min) |
| `backend/.env` | `ACCESS_TOKEN_EXPIRE_MINUTES=720` (não versionado) |
| `backend/app/controllers/page_controller.py` | Carrega `pecas` (loja e painel); admin no seletor de atribuição de OS |
| `backend/app/services/ordem_servico_service.py` | Correção das fontes de serviços/peças/movimentações da OS |
| `backend/app/services/movimentacao_estoque_service.py` | Saída financeira automática na movimentação manual |
| `backend/app/templates/base.html` | Inclui `session-timeout.js` |
| `backend/static/js/session-timeout.js` | **Novo** — logout por inatividade (1h) |
| `backend/app/templates/pages/painel.html` | Remove barra de navegação secundária |
| `backend/app/templates/partials/PedidoPanel.html` | Liga seletor de status e exclusão |
| `backend/app/templates/partials/ProdutoPanel.html` | Nova seção de Peças (CRUD + upload de foto) |
| `backend/app/templates/pages/loja.html` | Seções separadas "Produtos" e "Peças" |
| `backend/app/templates/pages/movimentacoes_financeiras.html` | Remove "ID de Pagamento" |
| `backend/static/js/movimentacoes_financeiras.js` | Remove lógica de "ID de Pagamento" |
| `backend/app/templates/pages/checkout.html` | Carrinho/retirada/forma de pagamento/botão |
| `backend/static/js/checkout.js` | Total sem frete, status pendente, limpar carrinho |

---

## Pontos a confirmar

### 1. Forma de Pagamento não é persistida
A "Forma de Pagamento" foi incluída como campo **obrigatório** no formulário de
checkout, mas **não é gravada** no banco. A tabela `pedido` não possui coluna para
essa informação, e a lista de ajustes não solicitou persistência — criar
coluna/migração/schema seria adicionar comportamento não pedido.

> **Se for desejado gravar a forma de pagamento no pedido**, é necessário: adicionar
> coluna em `pedido` (migração SQL), atualizar a entidade `Pedido`, os schemas
> `PedidoCreate/Public`, o repositório e enviar o campo no `checkout.js`. Posso
> implementar mediante confirmação.

### 2. Validade de 12h do token em produção
A validade do token é controlada por `ACCESS_TOKEN_EXPIRE_MINUTES`. O padrão no
código foi definido para `720` (12h) e o `.env` local foi atualizado. Porém o `.env`
é ignorado pelo Git, e o ambiente de produção (Cloud Run) normalmente define essa
variável pelas **variáveis de ambiente do GCP**.

> **Se houver `ACCESS_TOKEN_EXPIRE_MINUTES` configurado no Cloud Run / Secret
> Manager**, ele precisa ser atualizado para `720` lá também, senão o valor do
> ambiente sobrescreverá o padrão do código.
