# 🐶 DogMau Auto Center

> Sistema Web para Gestão de Oficinas Mecânicas

O **DogMau Auto Center** é um sistema web desenvolvido como projeto da disciplina de **Experiência Criativa: Implementando Sistemas de Informação**, com o objetivo de integrar, em uma única aplicação, os conhecimentos adquiridos ao longo da graduação em Engenharia de Software.

O projeto simula o funcionamento de uma oficina mecânica moderna, oferecendo recursos para gerenciamento de clientes, veículos, ordens de serviço, estoque, financeiro, orçamentos e vendas de produtos.

Durante a apresentação final da disciplina, o projeto foi reconhecido pela banca avaliadora, conquistando o **1º lugar entre todos os projetos apresentados**, destacando-se pela qualidade técnica, organização da arquitetura e abrangência das funcionalidades desenvolvidas.

Embora tenha sido concebido inicialmente para atender aos requisitos da disciplina, o sistema evoluiu continuamente após sua entrega, recebendo novas funcionalidades, melhorias arquiteturais e refatorações que o aproximam de um ambiente de produção.

---

# Sobre o Projeto

O DogMau Auto Center foi desenvolvido para centralizar todas as operações de uma oficina mecânica em um único sistema.

A plataforma permite controlar desde o cadastro de clientes até o fechamento financeiro dos serviços realizados, eliminando controles manuais e organizando todas as informações da oficina em um banco de dados único.

Entre os principais processos suportados pelo sistema estão:

- Cadastro de clientes
- Cadastro de veículos
- Controle de endereços
- Cadastro de marcas e modelos
- Abertura de ordens de serviço
- Elaboração de orçamentos
- Controle de estoque de peças
- Cadastro de produtos para venda
- Registro de pedidos
- Controle financeiro
- Registro de pagamentos
- Geração de relatórios gerenciais

Toda a comunicação entre a interface e o servidor ocorre por meio de uma **API REST**, permitindo que o frontend permaneça desacoplado da lógica de negócio.

---

# Objetivos

O desenvolvimento do sistema teve como principais objetivos:

- Aplicar os conhecimentos adquiridos durante a graduação em um projeto integrado.
- Simular o funcionamento completo de uma oficina mecânica.
- Desenvolver uma arquitetura baseada em API REST.
- Aplicar boas práticas de Engenharia de Software.
- Modelar um banco de dados relacional capaz de representar os processos do negócio.
- Implementar autenticação e autorização utilizando JWT.
- Utilizar serviços em nuvem para hospedagem da aplicação.
- Containerizar o backend utilizando Docker.
- Desenvolver uma aplicação organizada, escalável e de fácil manutenção.

---

# Principais Funcionalidades

## Gestão de Usuários

- Cadastro de clientes
- Cadastro de administradores
- Cadastro de mecânicos
- Controle de permissões por perfil
- Autenticação utilizando JWT
- Recuperação de senha
- Alteração de senha
- Upload de foto de perfil

---

## Gestão de Veículos

- Cadastro de veículos
- Associação entre veículo e proprietário
- Cadastro de marcas
- Cadastro de modelos
- Histórico de serviços

---

## Ordens de Serviço

- Abertura de ordens de serviço
- Associação ao cliente
- Associação ao veículo
- Atribuição de mecânico responsável
- Controle de status
- Inclusão de peças
- Inclusão de serviços
- Cálculo automático do valor total

---

## Orçamentos

- Criação de orçamentos
- Inclusão de peças
- Inclusão de serviços
- Aprovação ou rejeição
- Conversão em Ordem de Serviço

---

## Controle de Estoque

- Cadastro de peças
- Cadastro de produtos
- Controle de quantidade em estoque
- Registro de entradas
- Registro de saídas
- Histórico completo de movimentações

---

## Pedidos

- Cadastro de pedidos
- Associação de produtos
- Associação de peças
- Controle de status
- Atualização automática de estoque

---

## Financeiro

- Registro de pagamentos
- Movimentações financeiras
- Controle de entradas
- Controle de saídas
- Relatórios financeiros

---

## Relatórios

O sistema disponibiliza relatórios para acompanhamento da operação da oficina, incluindo:

- Faturamento
- Financeiro por período
- Ordens de Serviço
- Estoque
- Serviços realizados
- Dashboard gerencial
- Produtos mais vendidos
- Peças mais utilizadas

---

# Tecnologias Utilizadas

## Frontend

- HTML5
- CSS3
- JavaScript

---

## Backend

- Python
- FastAPI
- Uvicorn

---

## Banco de Dados

- PostgreSQL

---

## Infraestrutura

- Google Cloud Run
- Google Cloud SQL
- Firebase Hosting
- Docker

---

# Destaques do Projeto

- 🥇 1º lugar na banca da disciplina de Experiência Criativa.
- Arquitetura baseada em API REST.
- Backend estruturado em camadas (Routes, Services, Repositories e Schemas).
- Banco de dados relacional normalizado.
- Controle de permissões por papéis de usuário.
- Infraestrutura hospedada na Google Cloud Platform.
- Backend containerizado utilizando Docker.
- Projeto em constante evolução após a entrega da disciplina.

# Arquitetura do Sistema

O DogMau Auto Center foi desenvolvido seguindo uma arquitetura em camadas (Layered Architecture), separando responsabilidades entre interface, regras de negócio, acesso aos dados e infraestrutura.

Essa organização torna o sistema mais organizado, facilita a manutenção, reduz o acoplamento entre componentes e permite que novas funcionalidades sejam adicionadas com menor impacto sobre o restante da aplicação.

A aplicação é composta por três grandes componentes:

- Frontend
- Backend
- Banco de Dados

Toda a comunicação ocorre através de uma API REST, utilizando requisições HTTP e respostas em formato JSON.

---

# Arquitetura Geral

```text
                 Usuário
                    │
                    ▼
      HTML • CSS • JavaScript
       (Firebase Hosting)
                    │
              Requisições HTTP
                    │
                    ▼
      Google Cloud Run (FastAPI)
                    │
      ┌─────────────┼─────────────┐
      │             │             │
      ▼             ▼             ▼
   Rotas        Services     Middlewares
                    │
                    ▼
             Repositories
                    │
                    ▼
        PostgreSQL (Cloud SQL)
```

---

# Frontend

O frontend foi desenvolvido utilizando tecnologias nativas da Web, priorizando simplicidade, desempenho e facilidade de manutenção.

Tecnologias utilizadas:

- HTML5
- CSS3
- JavaScript

Toda a interface da aplicação é composta por páginas estáticas que consomem a API REST disponibilizada pelo backend.

O frontend possui telas para:

- Login
- Cadastro de usuários
- Dashboard
- Clientes
- Veículos
- Ordens de Serviço
- Orçamentos
- Estoque
- Produtos
- Peças
- Pedidos
- Financeiro
- Relatórios
- Perfil do usuário

O projeto foi originalmente desenvolvido dessa forma devido aos requisitos da disciplina de Experiência Criativa, que restringiam o uso de frameworks frontend.

Apesar disso, sua arquitetura permite uma futura migração para frameworks modernos, como React, sem necessidade de alterações significativas na API.

---

# Backend

O backend concentra toda a lógica de negócio da aplicação.

Foi desenvolvido utilizando Python e FastAPI, seguindo os princípios de separação de responsabilidades e organização por camadas.

Principais responsabilidades:

- autenticação
- autorização
- validações
- regras de negócio
- controle financeiro
- gerenciamento de estoque
- gerenciamento de usuários
- gerenciamento de veículos
- gerenciamento de pedidos
- gerenciamento de ordens de serviço
- integração com banco de dados
- geração de relatórios

A API segue o padrão REST, retornando respostas em formato JSON.

---

# Organização do Backend

A estrutura do backend foi organizada em módulos especializados.

```text
backend/
│
├── app/
│
├── routes/
│      Endpoints da API
│
├── services/
│      Regras de negócio
│
├── repositories/
│      Acesso ao banco de dados
│
├── schemas/
│      Validação utilizando Pydantic
│
├── models/
│      Entidades da aplicação
│
├── middlewares/
│      Autenticação e autorização
│
├── core/
│      Configurações, utilitários e segurança
│
└── main.py
```

Cada camada possui uma responsabilidade específica.

### Routes

Recebem as requisições HTTP, validam parâmetros e encaminham o processamento para os Services.

Não possuem regras de negócio.

---

### Services

Implementam toda a lógica da aplicação.

São responsáveis por:

- validações
- cálculos
- permissões
- regras de negócio
- integração entre diferentes módulos

Sempre que possível, as regras permanecem centralizadas nessa camada.

---

### Repositories

Realizam exclusivamente o acesso ao banco de dados.

São responsáveis por:

- SELECT
- INSERT
- UPDATE
- DELETE
- consultas especializadas

Essa separação evita que consultas SQL fiquem espalhadas pelo projeto.

---

### Schemas

Utilizam Pydantic para validar todos os dados recebidos pela API.

Entre as validações existentes estão:

- CPF/CNPJ
- Email
- Senha
- Datas
- Quantidades
- Valores monetários
- Campos obrigatórios

Isso garante que apenas dados válidos sejam processados.

---

### Middlewares

Os middlewares são responsáveis principalmente pelo processo de autenticação.

Entre suas funções estão:

- leitura do token JWT
- validação do usuário autenticado
- autorização baseada em papéis
- proteção das rotas privadas

---

# Controle de Permissões

O sistema utiliza controle de acesso baseado em papéis (RBAC - Role Based Access Control).

Atualmente existem três perfis de usuário.

| Papel | Descrição |
|--------|-----------|
| admin | Acesso completo ao sistema |
| mecanico | Execução e acompanhamento das Ordens de Serviço |
| cliente | Acesso aos próprios dados, veículos e pedidos |

As permissões são verificadas antes da execução de cada operação protegida.

---

# API REST

Toda a comunicação entre frontend e backend ocorre através de uma API REST.

As principais características da API são:

- requisições HTTP
- respostas JSON
- autenticação JWT
- validação utilizando Pydantic
- códigos HTTP padronizados
- documentação automática via Swagger/OpenAPI

A separação entre frontend e backend permite que outros clientes (como aplicativos móveis ou sistemas externos) consumam a mesma API futuramente.

---

# Banco de Dados

O banco de dados é relacional e utiliza PostgreSQL.

Todas as operações do sistema são persistidas no Cloud SQL, permitindo integridade referencial, controle transacional e consistência dos dados.

A modelagem foi construída seguindo princípios de normalização e utiliza relacionamentos entre entidades para representar os processos da oficina mecânica.

A próxima seção apresenta detalhadamente toda a modelagem do banco de dados.

# Modelagem do Banco de Dados

O DogMau Auto Center utiliza o **PostgreSQL** como Sistema Gerenciador de Banco de Dados (SGBD).

Toda a modelagem foi construída seguindo o modelo relacional, utilizando chaves primárias, chaves estrangeiras e regras de integridade referencial para garantir consistência entre as informações armazenadas.

O banco foi projetado para representar os principais processos existentes em uma oficina mecânica, desde o cadastro de clientes até o fechamento financeiro dos serviços realizados.

Entre as principais características da modelagem estão:

- Normalização dos dados
- Integridade referencial
- Separação por domínio de negócio
- Auditoria utilizando timestamps
- Soft Delete nas entidades principais
- Relacionamentos um-para-muitos e muitos-para-muitos

---

# Organização do Banco

As tabelas foram divididas em grandes módulos de negócio.

```text
Usuários
│
├── usuario
├── endereco
└── veiculo

Catálogo
│
├── marca
├── modelo
├── servico
├── produto
└── peca

Oficina
│
├── orcamento
├── orcamento_servico
├── orcamento_peca
├── ordem_servico
├── os_servico
└── os_peca

Vendas
│
├── pedido
├── pedido_produto
└── pedido_peca

Financeiro
│
├── pagamento
├── movimentacao_financeira
└── movimentacao_estoque
```

---

# Usuários

A tabela **usuario** representa todas as pessoas cadastradas no sistema.

Não existe uma tabela separada para clientes, administradores ou mecânicos.

O comportamento de cada usuário é definido através do campo **role**, permitindo que um mesmo modelo de dados represente diferentes perfis de acesso.

Papéis disponíveis:

- admin
- mecanico
- cliente

Principais informações armazenadas:

- nome
- email
- senha criptografada
- telefone
- CPF/CNPJ
- data de nascimento
- foto de perfil
- status de ativação

Relacionamentos:

```
usuario
   │
   ├── endereco
   ├── veiculo
   ├── orcamento
   ├── pedido
   └── ordem_servico
```

---

# Endereços

Cada usuário pode possuir um ou mais endereços cadastrados.

São armazenadas informações como:

- logradouro
- número
- CEP
- complemento
- bairro
- cidade
- estado

Relacionamento:

```
usuario (1)
      │
      └─────────── (N) endereco
```

---

# Marcas

Representa os fabricantes de veículos.

Exemplos:

- Volkswagen
- Chevrolet
- Fiat
- Toyota
- Honda

Além do nome da marca, podem ser armazenados:

- país de origem
- site oficial

Relacionamento:

```
marca (1)
      │
      └────────── (N) modelo
```

---

# Modelos

Representa os modelos comercializados por cada fabricante.

Exemplos:

- Gol
- Onix
- Corolla
- Civic
- Uno

Cada modelo pertence obrigatoriamente a uma marca.

Também podem ser registrados:

- categoria
- combustível
- ano de lançamento
- número de portas

Relacionamento:

```
modelo (1)
      │
      └────────── (N) veiculo
```

---

# Veículos

Cada veículo pertence a um único usuário.

São armazenados:

- placa
- cor
- ano de fabricação
- modelo

Relacionamentos:

```
usuario (1)
      │
      └────────── (N) veiculo

modelo (1)
      │
      └────────── (N) veiculo
```

---

# Serviços

Representa todos os serviços oferecidos pela oficina.

Exemplos:

- Troca de óleo
- Balanceamento
- Alinhamento
- Revisão completa
- Troca de correia

Cada serviço possui:

- nome
- descrição
- tempo estimado
- preço

Os serviços podem ser utilizados tanto em orçamentos quanto em Ordens de Serviço.

---

# Produtos

Produtos representam itens comercializados diretamente ao cliente.

Exemplos:

- Óleo de motor
- Aditivo
- Fluido de freio
- Limpador de para-brisa

Cada produto possui:

- nome
- descrição
- preço
- estoque
- imagem

Relacionamentos:

```
produto
      │
      └──────── pedido_produto
```

---

# Peças

As peças representam componentes utilizados durante manutenções.

Diferentemente dos produtos, elas possuem integração direta com Ordens de Serviço e Orçamentos.

Exemplos:

- Pastilha de freio
- Disco de freio
- Correia dentada
- Filtro de óleo
- Bateria

Cada peça possui:

- nome
- preço unitário
- quantidade em estoque
- imagem

Relacionamentos:

```
peca
   │
   ├── pedido_peca
   ├── orcamento_peca
   ├── os_peca
   └── movimentacao_estoque
```

---

# Diferença entre Produtos e Peças

Embora ambos possuam controle de estoque, representam conceitos distintos dentro do sistema.

**Produtos**

São itens vendidos diretamente ao cliente.

Exemplos:

- aromatizantes
- óleo
- palhetas
- acessórios

**Peças**

São componentes utilizados na execução de serviços mecânicos.

Exemplos:

- embreagem
- amortecedor
- correia
- rolamentos

Essa separação permite controlar de forma independente o estoque comercial e o estoque operacional da oficina.

# Processos Operacionais

As tabelas deste módulo representam o fluxo principal da oficina mecânica, desde a solicitação de um orçamento até a conclusão do serviço e seu respectivo pagamento.

O processo foi modelado para refletir o funcionamento de uma oficina real, permitindo acompanhar todas as etapas do atendimento ao cliente.

Fluxo simplificado:

```text
Cliente
    │
    ▼
Veículo
    │
    ▼
Orçamento
    │
    ├── Peças
    └── Serviços
    │
    ▼
Ordem de Serviço
    │
    ├── Mecânico responsável
    ├── Peças utilizadas
    ├── Serviços executados
    │
    ▼
Pagamento
    │
    ▼
Movimentação Financeira
```

---

# Orçamentos

A tabela **orcamento** representa a estimativa de custos elaborada antes da execução de um serviço.

Cada orçamento está associado a:

- um cliente
- um veículo

Além disso, possui informações como:

- status
- valor total
- datas de criação e atualização

O valor total é calculado automaticamente a partir das peças e serviços adicionados.

Relacionamentos:

```text
usuario (1)
      │
      └────────── (N) orcamento

veiculo (1)
      │
      └────────── (N) orcamento
```

---

# Itens do Orçamento

O sistema utiliza tabelas intermediárias para permitir que um orçamento contenha diversos itens.

## orcamento_peca

Relaciona peças ao orçamento.

Campos principais:

- orçamento
- peça
- quantidade

Relacionamento:

```text
orcamento
      │
      └─────── orcamento_peca ─────── peca
```

---

## orcamento_servico

Relaciona serviços ao orçamento.

Campos principais:

- orçamento
- serviço
- quantidade

Relacionamento:

```text
orcamento
      │
      └────── orcamento_servico ───── servico
```

Essas tabelas representam relacionamentos muitos-para-muitos entre orçamentos, peças e serviços.

---

# Ordens de Serviço

Após a aprovação de um orçamento, a oficina pode abrir uma Ordem de Serviço (OS).

A Ordem de Serviço representa o documento utilizado durante a execução do trabalho.

Cada OS possui:

- cliente
- veículo
- descrição do problema
- status
- valor total
- datas de abertura e conclusão

Além disso, pode possuir um mecânico responsável.

Relacionamento:

```text
usuario
      │
      └──────────── ordem_servico

veiculo
      │
      └──────────── ordem_servico
```

---

# Mecânicos

Os mecânicos não possuem uma tabela própria.

Eles são cadastrados normalmente na tabela **usuario**, diferenciando-se apenas pelo campo:

```text
role = mecanico
```

Quando um administrador atribui um mecânico a uma Ordem de Serviço, o sistema apenas associa o ID desse usuário à OS.

Essa abordagem reduz redundâncias e simplifica a modelagem do banco de dados.

---

# Peças utilizadas na Ordem de Serviço

Durante a execução do serviço, diversas peças podem ser utilizadas.

Essas informações são armazenadas na tabela **os_peca**.

Ela registra:

- ordem de serviço
- peça
- quantidade utilizada

Relacionamento:

```text
ordem_servico
        │
        └──────── os_peca ───────── peca
```

Sempre que uma peça é utilizada, o estoque pode ser atualizado automaticamente através das movimentações de estoque.

---

# Serviços executados

Da mesma forma, uma Ordem de Serviço pode conter diversos serviços.

Esses registros ficam armazenados em **os_servico**.

Campos:

- ordem de serviço
- serviço
- quantidade

Relacionamento:

```text
ordem_servico
        │
        └────── os_servico ────── servico
```

Essa estrutura permite que uma mesma OS possua quantos serviços forem necessários.

---

# Pedidos

Além dos serviços da oficina, o sistema também possui um módulo de vendas.

A tabela **pedido** representa compras realizadas pelos clientes.

Cada pedido possui:

- cliente
- valor total
- status

Relacionamento:

```text
usuario (1)
      │
      └──────── pedido (N)
```

---

# Produtos do Pedido

Os produtos vendidos são registrados através da tabela **pedido_produto**.

Cada registro informa:

- pedido
- produto
- quantidade

Relacionamento:

```text
pedido
     │
     └──────── pedido_produto ───────── produto
```

---

# 🔩 Peças do Pedido

O sistema também permite vender peças diretamente ao cliente.

Esses registros ficam em **pedido_peca**.

Relacionamento:

```text
pedido
     │
     └──────── pedido_peca ───────── peca
```

Dessa forma, um pedido pode conter simultaneamente:

- produtos
- peças

---

# Pagamentos

Após a conclusão de uma Ordem de Serviço, é possível registrar um pagamento.

Cada pagamento possui:

- Ordem de Serviço
- valor
- forma de pagamento
- status
- data do pagamento

Relacionamento:

```text
ordem_servico (1)
        │
        └──────── pagamento
```

Os pagamentos podem assumir diferentes estados, como:

- pendente
- pago
- cancelado

---

# Movimentações Financeiras

Todas as entradas e saídas financeiras da oficina são registradas na tabela **movimentacao_financeira**.

Cada movimentação armazena:

- tipo
- valor
- descrição
- pagamento relacionado (quando existir)

Relacionamento:

```text
pagamento
      │
      └────── movimentacao_financeira
```

Essa tabela permite gerar relatórios financeiros completos sem depender exclusivamente dos pagamentos.

---

# Movimentações de Estoque

O controle de estoque é realizado por meio da tabela **movimentacao_estoque**.

Sempre que ocorre uma entrada ou saída de peças, uma movimentação é registrada.

Cada registro armazena:

- peça
- tipo de movimentação
- quantidade
- motivo
- data

Exemplos de movimentações:

- Compra de peças
- Utilização em Ordem de Serviço
- Venda
- Ajuste de estoque
- Correção de inventário

Relacionamento:

```text
peca
   │
   └──────── movimentacao_estoque
```

Esse histórico permite rastrear toda a movimentação do estoque ao longo do tempo.

---

# Relatórios

O sistema utiliza as informações armazenadas nas tabelas operacionais para gerar indicadores e relatórios gerenciais.

Entre eles estão:

- Faturamento por período
- Saldo financeiro
- Movimentações financeiras
- Ordens de Serviço por status
- Serviços realizados
- Produtos mais vendidos
- Peças mais utilizadas
- Valor total do estoque
- Quantidade de serviços executados
- Dashboard administrativo

Os relatórios são gerados dinamicamente a partir das informações persistidas no banco de dados, dispensando armazenamento redundante e garantindo que os dados reflitam o estado atual da operação.

# Infraestrutura

O DogMau Auto Center foi desenvolvido utilizando uma arquitetura baseada em serviços da **Google Cloud Platform (GCP)**, permitindo que cada componente da aplicação seja executado de forma independente e escalável.

A infraestrutura foi planejada para separar interface, processamento e persistência de dados, facilitando a manutenção e futuras evoluções do sistema.

## Arquitetura da Infraestrutura

```text
                    Usuário
                       │
                       ▼
          Firebase Hosting (Frontend)
                       │
                 Requisições HTTPS
                       │
                       ▼
            Google Cloud Run (Backend)
                       │
              API REST (FastAPI)
                       │
                       ▼
          Google Cloud SQL (PostgreSQL)
```

---

## Firebase Hosting

O frontend da aplicação está hospedado utilizando o **Firebase Hosting**.

Essa solução oferece:

- Distribuição rápida de arquivos estáticos
- HTTPS automático
- Alta disponibilidade
- Fácil integração com aplicações web

Como o frontend foi desenvolvido utilizando HTML, CSS e JavaScript, o Firebase Hosting atende perfeitamente às necessidades do projeto.

---

## Google Cloud Run

O backend é executado no **Google Cloud Run**.

O serviço recebe todas as requisições HTTP enviadas pelo frontend, processa as regras de negócio e realiza a comunicação com o banco de dados.

Entre as vantagens da utilização do Cloud Run estão:

- Escalabilidade automática
- Deploy simplificado
- Execução baseada em containers Docker
- Baixo custo operacional
- Integração nativa com outros serviços da Google Cloud

---

## Google Cloud SQL

Toda a persistência de dados é realizada utilizando o **Cloud SQL**, serviço gerenciado da Google Cloud para bancos de dados relacionais.

O sistema utiliza:

- PostgreSQL

O Cloud SQL oferece:

- Backups automáticos
- Alta disponibilidade
- Gerenciamento simplificado
- Integração segura com o Cloud Run
- Monitoramento da infraestrutura

---

# Segurança

A aplicação implementa mecanismos de autenticação e autorização para proteger os recursos da API.

Entre eles:

- Autenticação utilizando JWT (JSON Web Token)
- Controle de acesso baseado em papéis (RBAC)
- Senhas armazenadas de forma criptografada
- Validação de dados utilizando Pydantic
- Proteção de rotas privadas por meio de Middlewares

Os papéis atualmente suportados são:

| Papel | Descrição |
|--------|-----------|
| **admin** | Acesso completo ao sistema |
| **mecanico** | Execução e acompanhamento das Ordens de Serviço |
| **cliente** | Acesso às próprias informações, veículos, pedidos e orçamentos |

---

# Organização do Projeto

O backend foi estruturado seguindo uma arquitetura em camadas, visando desacoplamento entre componentes e facilidade de manutenção.

```text
backend/
│
├── app/
│   ├── core/
│   ├── middlewares/
│   ├── models/
│   ├── repositories/
│   ├── routes/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   └── main.py
│
├── requirements.txt
├── Dockerfile
└── README.md
```

Cada camada possui uma responsabilidade bem definida:

| Camada | Responsabilidade |
|---------|------------------|
| Routes | Endpoints da API |
| Services | Regras de negócio |
| Repositories | Comunicação com o banco de dados |
| Schemas | Validação de dados |
| Models | Representação das entidades |
| Middlewares | Autenticação e autorização |
| Core | Configurações e componentes compartilhados |

Essa separação facilita testes, reutilização de código e futuras refatorações.

---

# Documentação da API

O backend utiliza o **FastAPI**, permitindo a geração automática da documentação da API.

As interfaces podem ser acessadas pelos seguintes endpoints:

```text
/swagger
```

Documentação interativa utilizando Swagger UI.

```text
/docs
```

Essas ferramentas permitem visualizar todos os endpoints disponíveis, seus parâmetros, exemplos de requisição e respostas esperadas.

---

# Trabalhos Futuros

Embora o sistema esteja plenamente funcional, algumas melhorias poderão ser incorporadas em versões futuras.

Entre elas:

- Migração do frontend para React
- Aplicativo mobile
- Integração com gateways de pagamento
- Sistema de notificações por e-mail
- Integração com WhatsApp
- Agendamento online
- Dashboard com gráficos interativos
- Controle de fornecedores
- Controle de compras
- Emissão de notas fiscais
- Integração com APIs automotivas

---

# Equipe

O DogMau Auto Center foi desenvolvido como projeto acadêmico da disciplina de **Experiência Criativa**, aplicando de forma integrada os conhecimentos adquiridos ao longo da graduação. Os responsáveis foram Julia Ferreira Padilha, Mateus Luiz Bailo, Ícaro Thiago Nunes e Bruno Hinz Cristiani.

O projeto continua evoluindo após sua entrega inicial, recebendo novas funcionalidades, melhorias arquiteturais e refatorações com o objetivo de aproximá-lo de um ambiente de produção.

---

# Licença

Este projeto foi desenvolvido para fins acadêmicos e educacionais.