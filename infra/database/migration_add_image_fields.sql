-- Campos de imagem para usuário, produto e peça
ALTER TABLE usuario ADD COLUMN IF NOT EXISTS foto_perfil VARCHAR(500);

ALTER TABLE produto ADD COLUMN IF NOT EXISTS imagem_produto VARCHAR(500);
ALTER TABLE peca ADD COLUMN IF NOT EXISTS imagem_peca VARCHAR(500);

-- Migração de coluna legada (se existir)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'produto' AND column_name = 'imagem'
    ) THEN
        UPDATE produto SET imagem_produto = imagem WHERE imagem_produto IS NULL AND imagem IS NOT NULL;
        ALTER TABLE produto DROP COLUMN imagem;
    END IF;
END $$;