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

-- Create a type for enum of genero
CREATE TYPE genero_type AS ENUM ('M', 'F', 'Outro');
-- Alter the doentes table to use the genero_type
ALTER TABLE doentes
    ALTER COLUMN genero TYPE genero_type USING genero::genero_type;

-- Create table for internamentos_unidade
CREATE TABLE IF NOT EXISTS internamentos_unidade (
    id SERIAL PRIMARY KEY,
    numero_ano INTEGER NOT NULL,
    doente_id INTEGER REFERENCES doentes(id),
    data_entrada TIMESTAMP NOT NULL,
    proveniencia VARCHAR(255),
    data_alta TIMESTAMP,
    destino VARCHAR(255),
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table proveniencia_destino
CREATE TABLE IF NOT EXISTS proveniencia_destino (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE,
    tipo VARCHAR(255) NOT NULL,
    localidade VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Alter internamentos_unidade to reference proveniencia_destino
ALTER TABLE internamentos_unidade
    ADD COLUMN proveniencia_id INTEGER REFERENCES proveniencia_destino(id),
    ADD COLUMN destino_id INTEGER REFERENCES proveniencia_destino(id);  

-- Alter internamentos_unidade to drop the old proveniencia and destino columns
ALTER TABLE internamentos_unidade
    DROP COLUMN proveniencia,
    DROP COLUMN destino;

