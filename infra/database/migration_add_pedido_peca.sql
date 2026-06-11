-- Relacionamento Pedido e Peças (e-commerce / loja)
-- Permite que um pedido contenha PEÇAS além de produtos, espelhando o padrão
-- de pedido_produto / os_peca / orcamento_peca.
CREATE TABLE IF NOT EXISTS pedido_peca (
    id_pedido INT NOT NULL,
    id_peca INT NOT NULL,
    quantidade INT DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (id_pedido, id_peca),
    CONSTRAINT fk_ped_peca_pedido FOREIGN KEY (id_pedido) REFERENCES pedido(id_pedido),
    CONSTRAINT fk_ped_peca_peca FOREIGN KEY (id_peca) REFERENCES peca(id_peca)
);
