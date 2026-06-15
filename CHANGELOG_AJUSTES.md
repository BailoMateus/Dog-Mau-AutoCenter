# Changelog de Ajustes — Dog Mau Auto Center

Data: 2026-06-10

Registro das correções e implementações realizadas conforme o documento de
requisitos. Para cada item: **causa raiz** encontrada, **correção aplicada** e
**arquivos** tocados.

## Decisões arquiteturais (confirmadas com o solicitante)

- **Imagens → Firebase Storage**: o `firebase-admin` já era dependência do
  projeto; as imagens passaram a ser persistidas no Storage (compatível com o
  filesystem efêmero do Cloud Run), mantendo as URLs no formato `/uploads/...`.
- **Peças em pedidos → nova tabela `pedido_peca`**: espelha o padrão de
  `pedido_produto` / `os_peca` / `orcamento_peca`. Requer migração no banco.

## Verificações executadas

- `import app.main` (a aplicação FastAPI sobe sem erros de import) — OK
- `python -m compileall app` nos arquivos Python — OK
- `node --check` nos JS alterados (`cart.js`, `loja.js`, `checkout.js`,
  `ordem_servico_detail.js`) — OK
- Parse de todos os templates Jinja alterados — OK
- Testes de lógica: fix do 500 da OS (linha enriquecida → entidade sem
  `TypeError`), round-trip de gravação/leitura de imagem e bloqueio de
  path-traversal — OK
- Não executado contra o banco/produção (Cloud SQL/Cloud Run) — depende das
  configurações listadas em "Dependências".

---

## 1. Imagens (perfil, produtos e peças)

- **Causa raiz:** o upload era gravado no **disco do container**
  (`backend/uploads/`, servido por `StaticFiles`). O Cloud Run tem
  **filesystem efêmero**: ao reciclar/escalar/hibernar a instância, os arquivos
  somem (e nem entram na imagem Docker, pois `uploads/` é ignorado pelo Git).
  Daí o `404` em `/uploads/pecas/...`. O fluxo de código (upload → DB →
  exibição) estava correto; faltava **armazenamento persistente**.
- **Correção:**
  - `save_image_upload` envia os bytes ao **Firebase Storage**
    (`uploads/<subdir>/<arquivo>`) e mantém o caminho `/uploads/...` no banco.
  - Nova rota `GET /uploads/{path}` serve a imagem lendo **do disco local OU do
    Storage** (`read_image_bytes`), com proteção contra *path traversal*.
  - **Fallback automático para disco** quando o Storage não está disponível
    (ex.: ambiente local sem credenciais) — sem mocks nem imagens padrão.
  - Exibição em vitrine, gerenciamento e perfil permanece com as mesmas URLs.
- **Arquivos:** `backend/app/core/file_storage.py`,
  `backend/app/core/firebase.py`, `backend/app/core/settings.py`,
  `backend/app/main.py`.

---

## 2. Painel de Gestão

### Aba Pedidos (Admin/Mecânico) — itens não carregavam
- **Causa raiz:** (a) o checkout falhava e os pedidos nasciam sem itens (ver
  Seção 5); (b) o banco **não possuía tabela de peças no pedido**, então peças
  nunca apareciam.
- **Correção:** criada a stack `pedido_peca`;
  `list_pedidos_detalhados` / `get_pedidos_detalhados_by_usuario` agregam
  **produtos e peças**; o `page_controller` repassa `itens_peca` e soma na
  contagem; o `order_card` lista produtos e peças com etiqueta de tipo.
- **Arquivos:** `backend/app/services/pedido_service.py`,
  `backend/app/controllers/page_controller.py`,
  `backend/app/templates/partials/components/order_card.html`.

### Fluxo de Orçamento → Ordem de Serviço automática
- A criação automática da OS ao **aprovar** um orçamento já existia (cria a OS e
  copia peças/serviços do orçamento). Mantido e confirmado funcional.
- **Arquivo (sem alteração):** `backend/app/services/orcamento_approval_service.py`.

### Ordem de Serviço — erro 500 na tela de detalhes
- **Causa raiz:** `GET /ordens-servico/{id}` retorna colunas enriquecidas por
  JOIN (`placa`, `cor`, `nome_modelo`, `proprietario_nome`, `mecanico_nome`,
  `orcamento_status`). O conversor fazia `OrdemServico(**row)`, e essas chaves
  extras **não são campos da dataclass** → `TypeError` → 500.
- **Correção:** `dict_to_ordem_servico` (e `dict_to_peca` /
  `dict_to_pedido_peca`) passaram a filtrar somente os campos válidos da
  dataclass (`_filter_fields`). Também ajustada a rota de movimentações no
  `ordem_servico_detail.js` para `/ordens-servico/{id}/pecas/movimentacoes`
  (rota real do backend). Carrega e exibe todos os dados da OS.
- **Arquivos:** `backend/app/models/entities.py`,
  `backend/static/js/ordem_servico_detail.js`.

### Atribuição de responsável (Administradores e Mecânicos)
- **Causa raiz:** o `OSPanel.html` usava o campo inexistente
  `os.id_mecanico_responsavel` e, após atribuir, o `select` reaparecia em vez de
  **refletir** o responsável atual. (O backend já persistia e já aceitava admin
  **e** mecânico como responsável.)
- **Correção:** a célula passou a exibir **"Responsável: <nome>"** (reflete após
  salvar) e oferece o `select` pré-selecionado no responsável atual para
  (re)atribuir enquanto a OS não estiver concluída/cancelada. `PATCH
  /ordens-servico/{id}/atribuir-mecanico` persiste no banco.
- **Arquivo:** `backend/app/templates/partials/OSPanel.html`.

---

## 3. Movimentações Financeiras (automáticas)

- **Venda de produto (pedido concluído):** gera **ENTRADA = soma dos produtos**.
- **Venda de peça (pedido concluído):** gera **ENTRADA = soma das peças**
  (lançamento separado, conforme requisito). As somas usam as tabelas de itens.
  - Correção adicional: removida a **baixa de estoque em dobro** — o estoque já é
    baixado quando o item é adicionado ao pedido; a baixa redundante na conclusão
    foi removida.
- **Conclusão de OS:** mantida a **ENTRADA = valor total da OS**.
- **Movimentação manual de estoque:** gera **SAÍDA financeira (valor de
  aquisição) apenas na ENTRADA manual**. Foi removida a saída financeira
  indevida que também era criada na saída de estoque.
- **Arquivos:** `backend/app/services/pedido_service.py`,
  `backend/app/services/movimentacao_estoque_service.py`,
  `backend/app/services/ordem_servico_service.py` (conclusão já existente).

---

## 4. Produtos, Peças e Carrinho (loja)

### Botões e comportamento
- **Causa raiz:** o `loja.js` adicionava o item com chaves erradas
  (`name`/`price`), mas o `cart.js` lia `nome`/`preco` → itens entravam com
  `preco: undefined` (Total = `NaN`). Além disso, redirecionava para `/checkout`
  ao adicionar; **peças não tinham botão**; produtos exibiam **"Comprar"**.
- **Correção:**
  - `cart.js` reescrito com itens **tipados** (`tipo` produto/peça, chave
    composta `tipo:id`) e normalização robusta de itens antigos.
  - `loja.js` envia as chaves corretas, **permanece na tela** (toast, sem
    redirecionar para checkout/carrinho) e trata **produtos e peças**.
  - `product_card.html`: texto **"Comprar" → "Adicionar ao Carrinho"**.
  - `loja.html`: adicionado botão **"Adicionar ao Carrinho"** nos cards de peça.
- **Arquivos:** `backend/static/js/cart.js`, `backend/static/js/loja.js`,
  `backend/app/templates/partials/components/product_card.html`,
  `backend/app/templates/pages/loja.html`.

---

## 5. Finalizar Compra (checkout)

- **Causa raiz:** com `preco` `undefined`, o **Total** era `NaN` e o
  `POST /api/pedidos` enviava `valor_total` inválido → erro ao "Finalizar
  Pedido". Os itens só suportavam `id_produto`.
- **Correção:** `checkout.js` renderiza **produtos e peças**, calcula o **Total**
  corretamente, cria o pedido (status **pendente**, associado ao usuário pelo
  token), envia produtos para `/api/pedidos/{id}/itens/` e **peças** para
  `/api/pedidos/{id}/pecas`, **limpa o carrinho** e exibe a mensagem
  **"Pedido feito com sucesso."**. O pedido fica visível a admin/mecânico na
  aba Pedidos.
- **Arquivos:** `backend/static/js/checkout.js`,
  `backend/app/templates/pages/checkout.html`.

---

## Stack nova: `pedido_peca` (peças no pedido)

Permite que um pedido contenha peças (carrinho, checkout, exibição e
financeiro). Criada espelhando `pedido_produto`.

- **Migração:** `infra/database/migration_add_pedido_peca.sql`
- **Entidade/conversor:** `PedidoPeca` + `dict_to_pedido_peca` em
  `backend/app/models/entities.py`
- **Repositório:** `backend/app/repositories/pedido_peca_repository.py`
- **Schema:** `backend/app/schemas/pedido_peca_schema.py`
- **Serviço:** `backend/app/services/pedido_peca_service.py`
- **Controller:** `backend/app/controllers/pedido_peca_controller.py`
  (`POST/GET /api/pedidos/{pedido_id}/pecas`)
- **Registro do router:** `backend/app/main.py`
- **Recalcular total:** `pedido_produto_service` passou a somar **produtos +
  peças** ao recalcular `valor_total` (evita perder o valor das peças quando o
  último item adicionado é um produto).

---

## Arquivos alterados (resumo)

| Arquivo | Mudança |
|---|---|
| `backend/app/core/settings.py` | Nova config `firebase_storage_bucket` |
| `backend/app/core/firebase.py` | `get_bucket()` + bucket do Storage |
| `backend/app/core/file_storage.py` | Upload/leitura via Firebase Storage (fallback disco) |
| `backend/app/main.py` | Rota `GET /uploads/{path}`; registro do router de peças do pedido |
| `backend/app/models/entities.py` | `_filter_fields` (fix 500 da OS); entidade `PedidoPeca` |
| `backend/app/services/movimentacao_estoque_service.py` | Saída financeira só na entrada manual |
| `backend/app/services/pedido_service.py` | Entrada por produtos e por peças; fim da baixa em dobro; agrega `itens_peca` |
| `backend/app/services/pedido_produto_service.py` | Recalcula total com produtos + peças |
| `backend/app/controllers/page_controller.py` | Repassa `itens_peca` e soma na contagem de itens |
| `backend/app/templates/pages/loja.html` | Botão "Adicionar ao Carrinho" nas peças |
| `backend/app/templates/pages/checkout.html` | Mensagem "Pedido feito com sucesso." |
| `backend/app/templates/partials/OSPanel.html` | Atribuição reflete o responsável atual |
| `backend/app/templates/partials/components/product_card.html` | "Comprar" → "Adicionar ao Carrinho" |
| `backend/app/templates/partials/components/order_card.html` | Lista produtos e peças do pedido |
| `backend/static/js/cart.js` | Itens tipados (produto/peça), correção de chaves |
| `backend/static/js/loja.js` | Chaves corretas, permanece na tela, trata peças |
| `backend/static/js/checkout.js` | Renderiza/envia produtos e peças; total correto |
| `backend/static/js/ordem_servico_detail.js` | Rota correta de movimentações |
| `backend/app/repositories/pedido_peca_repository.py` | **Novo** |
| `backend/app/schemas/pedido_peca_schema.py` | **Novo** |
| `backend/app/services/pedido_peca_service.py` | **Novo** |
| `backend/app/controllers/pedido_peca_controller.py` | **Novo** |
| `infra/database/migration_add_pedido_peca.sql` | **Novo** |

---

## Dependências / configuração necessárias

1. **Migração do banco (obrigatória):** aplicar
   `infra/database/migration_add_pedido_peca.sql` no Cloud SQL. Sem ela,
   adicionar peça ao pedido falha.
2. **Firebase Storage (produção):** definir a variável de ambiente
   `FIREBASE_STORAGE_BUCKET` no Cloud Run com o bucket real do projeto
   (ex.: `dog-mau-autocenter.appspot.com`; conferir em *Firebase Console →
   Storage* — projetos novos podem usar `.firebasestorage.app`). A service
   account de `firebase-credentials.json` precisa de permissão de Storage
   (*Storage Object Admin*). Sem isso, o backend usa o disco efêmero como
   fallback e o `404` volta em produção.
3. **Dependências Python:** já constam em `requirements.txt` (a imagem Docker as
   instala). Em execução local fora do container, garanta `python-multipart` e
   `jinja2` instalados.
4. Nenhuma biblioteca/arquitetura existente foi substituída; layouts e estilos
   foram preservados (apenas os textos/elementos exigidos pelos requisitos).
