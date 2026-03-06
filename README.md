# DogMau Auto Center

## Sistema de Gestão para Oficina Mecânica

O **DogMau Auto Center** é um sistema web desenvolvido como **projeto acadêmico** com o objetivo de simular a gestão completa de uma oficina mecânica. A aplicação centraliza processos operacionais como cadastro de clientes, controle de veículos, ordens de serviço, estoque de peças, agendamentos e controle financeiro.

O sistema foi projetado seguindo uma arquitetura baseada em **API REST**, utilizando serviços em nuvem para infraestrutura e armazenamento de dados.

Este projeto tem como objetivo aplicar conceitos de:

- Desenvolvimento Backend
- Modelagem de Banco de Dados
- Arquitetura em Nuvem
- APIs REST
- Controle de Autenticação e Permissões
- Containerização de aplicações

---

# Arquitetura do Sistema

O sistema foi estruturado em três camadas principais.

## Frontend

Responsável pela interface com o usuário.

Tecnologias utilizadas:

- HTML5
- CSS3
- JavaScript

O frontend realiza requisições HTTP para a API do backend, consumindo os endpoints responsáveis pela lógica da aplicação.

Hospedagem:

- Firebase Hosting

---

## Backend

Responsável pela lógica de negócio da aplicação e comunicação com o banco de dados.

Tecnologias utilizadas:

- Python
- FastAPI
- Uvicorn
- Docker

O backend expõe uma **API REST** responsável por:

- autenticação de usuários
- gerenciamento de clientes
- controle de veículos
- gerenciamento de ordens de serviço
- controle de estoque
- controle financeiro
- gerenciamento de agendamentos
- gerenciamento de pedidos do e-commerce

Hospedagem:

- Google Cloud Run

---

## Banco de Dados

O sistema utiliza **PostgreSQL** como banco de dados relacional.

Hospedagem:

- Google Cloud SQL

A modelagem foi construída utilizando boas práticas de banco de dados, incluindo:

- uso de chaves primárias e estrangeiras
- normalização de entidades
- rastreamento de auditoria em todas as tabelas

Todas as tabelas possuem os campos:

- `created_at`
- `updated_at`
- `deleted_at`

---

# Infraestrutura em Nuvem

A infraestrutura foi projetada utilizando serviços da **Google Cloud Platform (GCP)**.

Serviços utilizados:

| Serviço | Função |
|------|------|
| Cloud Run | Execução do backend |
| Cloud SQL | Banco de dados PostgreSQL |
| Firebase Hosting | Hospedagem do frontend |
| Artifact Registry | Armazenamento de imagens Docker |
| Secret Manager | Armazenamento seguro de credenciais |

Essa arquitetura permite escalabilidade, segurança e fácil manutenção do sistema.

---

# Modelagem do Banco de Dados

O sistema possui diversas entidades responsáveis por representar as operações da oficina.

## Usuários

- usuario

Responsável pelo controle de acesso ao sistema e autenticação.

---

## Clientes e Veículos

- cliente
- endereco
- veiculo
- marca
- modelo

Essas tabelas armazenam informações sobre clientes e seus veículos cadastrados na oficina.

---

## Operação da Oficina

- mecanico
- servico
- ordem_servico
- os_servico
- os_peca

Essas entidades registram os serviços realizados, peças utilizadas e o histórico de manutenção dos veículos.

---

## Controle de Estoque

- peca
- movimentacao_estoque

Responsáveis pelo controle das peças disponíveis e pelo registro de entradas e saídas de estoque.

---

## Orçamentos

- orcamento
- orcamento_servico
- orcamento_peca

Permitem gerar orçamentos antes da execução de uma ordem de serviço.

---

## Financeiro

- pagamento
- movimentacao_financeira

Registram os pagamentos realizados e movimentações financeiras da oficina.

---

## Agendamento

- agendamento

Permite registrar e gerenciar agendamentos de serviços para clientes.

---

## E-commerce

- produto
- pedido
- pedido_produto

Permitem a venda de produtos diretamente pelo sistema.

---

# Funcionalidades do Sistema

O sistema possui diversas funcionalidades voltadas para a gestão da oficina.

## Autenticação

- Login de usuários
- Autenticação via JWT
- Controle de permissões

---

## Gestão de Clientes

- Cadastro de clientes
- Cadastro de endereços
- Consulta de clientes

---

## Gestão de Veículos

- Cadastro de veículos
- Associação de veículos a clientes
- Consulta de histórico de serviços

---

## Ordens de Serviço

- Abertura de ordem de serviço
- Registro do problema do veículo
- Associação de mecânico responsável
- Inclusão de serviços executados
- Inclusão de peças utilizadas
- Atualização do status da ordem

---

## Orçamentos

- Criação de orçamento
- Inclusão de serviços
- Inclusão de peças
- Cálculo do valor total
- Aprovação do orçamento

---

## Controle de Estoque

- Cadastro de peças
- Controle de quantidade disponível
- Registro de entradas e saídas

---

## Financeiro

- Registro de pagamentos
- Registro de movimentações financeiras
- Consulta de faturamento

---

## Agendamento

- Criação de agendamentos
- Alteração de horários
- Cancelamento de agendamentos

---

## E-commerce

- Cadastro de produtos
- Criação de pedidos
- Associação de produtos ao pedido
- Atualização automática de estoque

---

# Desenvolvimento

Durante o desenvolvimento, os integrantes podem executar o backend localmente e conectar-se ao banco de dados hospedado no Cloud SQL.

Ferramentas recomendadas:

- DBeaver
- pgAdmin

---

# Deploy

## Backend

O backend é empacotado em uma imagem Docker e enviado para o Artifact Registry.

O deploy é realizado utilizando o comando:
