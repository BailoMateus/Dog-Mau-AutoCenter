-- Seed de usuario admin para ambiente LOCAL de desenvolvimento.
-- Executado automaticamente pelo docker-compose no primeiro boot do Postgres.
--
-- Credenciais de acesso:
--   Email: admin@dogmau.com
--   Senha: Senha123
--
-- Hash bcrypt gerado com:
--   python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('Senha123'))"
--
-- ATENCAO: este seed e EXCLUSIVO para ambiente local. NUNCA rodar em producao.

INSERT INTO usuario (nome, email, senha_hash, role, ativo)
VALUES (
    'Admin Local',
    'admin@dogmau.com',
    '$2b$12$KKREjFZ9DhFcxPDoYj1fa.wZFl5isJS1nwr3nKKtoFOUq.wkWHKr2',
    'admin',
    TRUE
)
ON CONFLICT (email) DO NOTHING;
