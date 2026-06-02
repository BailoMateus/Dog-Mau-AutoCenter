-- Permite OS sem responsável e atribuição a admin ou mecânico (tabela usuario)
ALTER TABLE ordem_servico DROP CONSTRAINT IF EXISTS fk_os_mecanico;

ALTER TABLE ordem_servico ALTER COLUMN id_usuario DROP NOT NULL;

ALTER TABLE ordem_servico
    ADD CONSTRAINT fk_os_responsavel
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario);
