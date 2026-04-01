-- Initial schema for the unidade database
CREATE TABLE IF NOT EXISTS doentes (
    id SERIAL PRIMARY KEY,
    numero_processo VARCHAR(255) NOT NULL UNIQUE,
    nome VARCHAR(255) NOT NULL,
    data_nascimento DATE NOT NULL,
    genero VARCHAR(50),
    morada VARCHAR(255),
    codigo_postal VARCHAR(20),
    localidade VARCHAR(100),
    contacto_telefone VARCHAR(20),
    contacto_email VARCHAR(255),
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);