-- Relacionamentos serviço → peça/produto e rastreio de OS em movimentações de estoque

-- Movimentação de estoque vinculada à OS
ALTER TABLE movimentacao_estoque
ADD COLUMN IF NOT EXISTS id_os INT;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_movimentacao_os'
    ) THEN
        ALTER TABLE movimentacao_estoque
        ADD CONSTRAINT fk_movimentacao_os
        FOREIGN KEY (id_os) REFERENCES ordem_servico(id_os);
    END IF;
END $$;

-- Peças consumidas por serviço (catálogo)
CREATE TABLE IF NOT EXISTS servico_peca (
    id_servico INT NOT NULL,
    id_peca INT NOT NULL,
    quantidade INT DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_servico, id_peca),
    CONSTRAINT fk_servico_peca_servico FOREIGN KEY (id_servico) REFERENCES servico(id_servico),
    CONSTRAINT fk_servico_peca_peca FOREIGN KEY (id_peca) REFERENCES peca(id_peca)
);

-- Produtos consumidos por serviço (catálogo)
CREATE TABLE IF NOT EXISTS servico_produto (
    id_servico INT NOT NULL,
    id_produto INT NOT NULL,
    quantidade INT DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_servico, id_produto),
    CONSTRAINT fk_servico_produto_servico FOREIGN KEY (id_servico) REFERENCES servico(id_servico),
    CONSTRAINT fk_servico_produto_produto FOREIGN KEY (id_produto) REFERENCES produto(id_produto)
);

-- id_produto opcional em movimentacao_estoque (se ainda não existir)
ALTER TABLE movimentacao_estoque
ALTER COLUMN id_peca DROP NOT NULL;

ALTER TABLE movimentacao_estoque
ADD COLUMN IF NOT EXISTS id_produto INT;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_movimentacao_produto'
    ) THEN
        ALTER TABLE movimentacao_estoque
        ADD CONSTRAINT fk_movimentacao_produto
        FOREIGN KEY (id_produto) REFERENCES produto(id_produto);
    END IF;
END $$;
