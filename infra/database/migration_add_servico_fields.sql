-- Campos adicionais do catálogo de serviços
ALTER TABLE servico ADD COLUMN IF NOT EXISTS nome_servico VARCHAR(150);
ALTER TABLE servico ADD COLUMN IF NOT EXISTS tempo_estimado VARCHAR(50);

UPDATE servico
SET nome_servico = LEFT(descricao, 150)
WHERE nome_servico IS NULL OR nome_servico = '';
