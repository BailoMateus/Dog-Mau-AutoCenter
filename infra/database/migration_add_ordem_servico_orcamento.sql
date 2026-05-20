ALTER TABLE ordem_servico
ADD COLUMN id_orcamento INT;

ALTER TABLE ordem_servico
ADD COLUMN valor_total DECIMAL(12,2) DEFAULT 0.00;

ALTER TABLE ordem_servico
ADD CONSTRAINT fk_os_orcamento FOREIGN KEY (id_orcamento) REFERENCES orcamento(id_orcamento);
