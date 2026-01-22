-- Extensão para criptografia
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Tabela de usuários da aplicação
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

-- Usuário inicial da aplicação
INSERT INTO users (username, password)
VALUES ('sales', crypt('teste123', gen_salt('bf')))
ON CONFLICT (username) DO NOTHING;

-- Permissão para usuários dinâmicos do Vault
GRANT SELECT ON users TO PUBLIC;

