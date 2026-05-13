-- Migration Script: Unificar cliente e mecanico em tabela usuario
-- Este script migra dados das tabelas cliente e mecanico para a tabela usuario unificada
-- e atualiza todas as referências de foreign keys

-- 1. Adicionar colunas de cliente à tabela usuario (se ainda não existirem)
DO $$
BEGIN
    -- Verificar se as colunas já existem antes de adicionar
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'usuario' AND column_name = 'telefone'
    ) THEN
        ALTER TABLE usuario ADD COLUMN telefone VARCHAR(20);
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'usuario' AND column_name = 'cpf_cnpj'
    ) THEN
        ALTER TABLE usuario ADD COLUMN cpf_cnpj VARCHAR(18);
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'usuario' AND column_name = 'data_nascimento'
    ) THEN
        ALTER TABLE usuario ADD COLUMN data_nascimento DATE;
    END IF;
END $$;

-- 2. Migrar dados da tabela cliente para usuario
INSERT INTO usuario (
    nome, 
    email, 
    senha_hash, 
    role, 
    ativo, 
    telefone, 
    cpf_cnpj, 
    data_nascimento,
    created_at,
    updated_at,
    deleted_at
)
SELECT 
    nome,
    COALESCE(email, 'cliente_' || id_cliente || '@temp.local'), -- Email temporário se nulo
    'temp_password_hash', -- Senha temporária que deve ser alterada
    'CLIENTE',
    COALESCE(ativo, true),
    telefone,
    cpf_cnpj,
    data_nascimento,
    created_at,
    updated_at,
    deleted_at
FROM cliente
WHERE deleted_at IS NULL;

-- 3. Migrar dados da tabela mecanico para usuario
INSERT INTO usuario (
    nome, 
    email, 
    senha_hash, 
    role, 
    ativo,
    created_at,
    updated_at,
    deleted_at
)
SELECT 
    nome,
    'mecanico_' || id_mecanico || '@temp.local', -- Email temporário
    'temp_password_hash', -- Senha temporária que deve ser alterada
    'MECANICO',
    COALESCE(ativo, true),
    created_at,
    updated_at,
    deleted_at
FROM mecanico
WHERE deleted_at IS NULL;

-- 4. Criar tabela de mapeamento de IDs antigos para novos
CREATE TABLE IF NOT EXISTS migration_id_mapping (
    old_table VARCHAR(20) NOT NULL,
    old_id INT NOT NULL,
    new_usuario_id INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (old_table, old_id)
);

-- 5. Preencher tabela de mapeamento para clientes
INSERT INTO migration_id_mapping (old_table, old_id, new_usuario_id)
SELECT 'cliente', id_cliente, id_usuario
FROM cliente c
JOIN usuario u ON u.nome = c.nome AND u.email LIKE 'cliente_%@temp.local'
WHERE c.deleted_at IS NULL;

-- 6. Preencher tabela de mapeamento para mecânicos
INSERT INTO migration_id_mapping (old_table, old_id, new_usuario_id)
SELECT 'mecanico', id_mecanico, id_usuario
FROM mecanico m
JOIN usuario u ON u.nome = m.nome AND u.email LIKE 'mecanico_%@temp.local'
WHERE m.deleted_at IS NULL;

-- 7. Atualizar foreign keys em tabelas relacionadas
-- Endereços
UPDATE endereco 
SET id_usuario = m.new_usuario_id
FROM migration_id_mapping m
WHERE m.old_table = 'cliente' 
  AND endereco.id_cliente = m.old_id;

-- Veículos
UPDATE veiculo 
SET id_usuario = m.new_usuario_id
FROM migration_id_mapping m
WHERE m.old_table = 'cliente' 
  AND veiculo.id_cliente = m.old_id;

-- Ordens de Serviço (atualizar id_mecanico para id_usuario)
UPDATE ordem_servico 
SET id_mecanico = m.new_usuario_id
FROM migration_id_mapping m
WHERE m.old_table = 'mecanico' 
  AND ordem_servico.id_mecanico = m.old_id;

-- Orçamentos
UPDATE orcamento 
SET id_usuario = m.new_usuario_id
FROM migration_id_mapping m
WHERE m.old_table = 'cliente' 
  AND orcamento.id_cliente = m.old_id;

-- Agendamentos
UPDATE agendamento 
SET id_usuario = m.new_usuario_id
FROM migration_id_mapping m
WHERE m.old_table = 'cliente' 
  AND agendamento.id_cliente = m.old_id;

-- Pedidos
UPDATE pedido 
SET id_usuario = m.new_usuario_id
FROM migration_id_mapping m
WHERE m.old_table = 'cliente' 
  AND pedido.id_cliente = m.old_id;

-- 8. Remover colunas antigas de foreign keys (opcional, após verificar migração)
-- Descomente as linhas abaixo após confirmar que a migração foi bem-sucedida
/*
ALTER TABLE endereco DROP COLUMN IF EXISTS id_cliente;
ALTER TABLE veiculo DROP COLUMN IF EXISTS id_cliente;
ALTER TABLE ordem_servico DROP COLUMN IF EXISTS id_mecanico;
ALTER TABLE orcamento DROP COLUMN IF EXISTS id_cliente;
ALTER TABLE agendamento DROP COLUMN IF EXISTS id_cliente;
ALTER TABLE pedido DROP COLUMN IF EXISTS id_cliente;
*/

-- 9. Remover tabelas antigas (opcional, após verificar migração)
-- Descomente as linhas abaixo após confirmar que a migração foi bem-sucedida
/*
DROP TABLE IF EXISTS cliente CASCADE;
DROP TABLE IF EXISTS mecanico CASCADE;
*/

-- 10. Limpar tabela de mapeamento (opcional)
-- Descomente a linha abaixo após confirmar que a migração foi bem-sucedida
-- DROP TABLE IF EXISTS migration_id_mapping;

-- Notas importantes:
-- 1. Todos os usuários migrados terão senhas temporárias "temp_password_hash"
--    que devem ser alteradas no primeiro login
-- 2. Emails temporários foram criados para clientes e mecânicos sem email
-- 3. Verifique manualmente os dados migrados antes de remover as tabelas antigas
-- 4. Faça backup do banco de dados antes de executar este script
