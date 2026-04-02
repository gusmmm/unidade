# Unidade - Localhost Fullstack Application

Sistema localhost-first com PostgreSQL em Docker, FastAPI backend e Streamlit multipage frontend.

## Stack

- **Dependencies**: `uv` para gestão de pacotes
- **Database**: PostgreSQL em container Docker
- **Backend**: FastAPI
- **Frontend**: Streamlit (multipage)

## Arquitetura

```
unidade/
├── backend/          # FastAPI app
│   ├── core/         # config, security
│   ├── db/           # session, models
│   ├── schemas/      # Pydantic schemas
│   ├── repositories/ # data access
│   ├── services/     # business logic
│   ├── routers/      # API endpoints
│   └── tests/        # tests
├── frontend/         # Streamlit multipage
│   ├── pages/        # app pages
│   └── shared/       # components
├── db/               # migrations, seeds
└── docker-compose.yml
```

## Setup Local

```bash
# 1. Clonar e entrar no diretorio
cd unidade

# 2. Criar .env a partir do template
cp .env.example .env

# 3. Subir containers
docker-compose up -d

# 4. Instalar dependencias Python
uv sync

# 5. Correr backend
uv run uvicorn backend.main:app --reload --port 8000

# 6. Correr frontend (outro terminal)
uv run streamlit run frontend/main.py
```

## Autenticação

- Basic auth com password hashing
- Rotas de escrita protegidas
- Login/logout com session state

## Módulos

- **Doentes**: Gestão de pacientes
- **Internamentos**: Registos de internamento
- **Trauma/Queimaduras**: Dados clínicos
- **Microbiologia**: Resultados laboratoriais
- **Procedimentos**: Registos de procedimentos
- **Antecedentes/Problemas/Infeções**: Histórico clínico
- **Lookup Admin**: Gestão de tabelas de referência

## UI Standards

- Dropdowns para FKs (id + nome)
- Date/date-time widgets para campos clínicos
- Botões de ação (create/update/delete)
- Design system consistente

## Comandos Úteis

```bash
# Backup DB
docker exec unidade-db pg_dump -U postgres unidade > backup_$(date +%Y%m%d).sql

# Restore DB
cat backup.sql | docker exec -i unidade-db psql -U postgres unidade

# Ver logs backend
docker-compose logs -f backend

# Ver logs frontend
docker-compose logs -f frontend
```

## Development

```bash
# Run tests
uv run pytest

# Lint
uv run ruff check .

# Type check
uv run mypy .
```
