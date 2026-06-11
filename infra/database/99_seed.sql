-- Inserindo um usuário Admin inicial
INSERT INTO usuario (nome, email, password, role, ativo) VALUES 
('Administrador', 'admin@dogmau.com', '$2b$12$R.S2.wHk8Xh.Y4f3sZl6yO9.fP7t1tM2JzM.8.W/vF/mJt1H4hTz2', 'ADMIN', true)
ON CONFLICT (email) DO NOTHING;
-- A senha acima é 'admin123' em bcrypt (gerada para propósitos de teste)

-- Inserindo um usuário Cliente inicial
INSERT INTO usuario (nome, email, password, role, ativo, telefone, cpf_cnpj) VALUES 
('Cliente Teste', 'cliente@teste.com', '$2b$12$R.S2.wHk8Xh.Y4f3sZl6yO9.fP7t1tM2JzM.8.W/vF/mJt1H4hTz2', 'CLIENTE', true, '11999999999', '12345678901')
ON CONFLICT (email) DO NOTHING;

-- Inserindo algumas marcas
INSERT INTO marca (nome) VALUES ('Toyota'), ('Honda'), ('Chevrolet'), ('Ford'), ('Volkswagen') ON CONFLICT (nome) DO NOTHING;

-- Inserindo algumas categorias de serviços
INSERT INTO servico (nome, descricao, valor_base) VALUES 
('Troca de Óleo', 'Troca de óleo do motor e filtro', 150.00),
('Alinhamento e Balanceamento', 'Alinhamento de direção e balanceamento das 4 rodas', 120.00),
('Revisão Geral', 'Revisão preventiva de 10.000km', 450.00)
ON CONFLICT DO NOTHING;
