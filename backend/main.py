import os
from datetime import date, datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

import psycopg
from psycopg.rows import dict_row

app = FastAPI(title="Unidade API")


class DoenteBase(BaseModel):
    numero_processo: str
    nome: str
    data_nascimento: date
    genero: str | None = None
    morada: str | None = None
    codigo_postal: str | None = None
    localidade: str | None = None
    contacto_telefone: str | None = None
    contacto_email: str | None = None
    observacoes: str | None = None


class DoenteCreate(DoenteBase):
    pass


class DoenteUpdate(DoenteBase):
    pass


class DoentePatch(BaseModel):
    numero_processo: str | None = None
    nome: str | None = None
    data_nascimento: date | None = None
    genero: str | None = None
    morada: str | None = None
    codigo_postal: str | None = None
    localidade: str | None = None
    contacto_telefone: str | None = None
    contacto_email: str | None = None
    observacoes: str | None = None


class DoenteOut(DoenteBase):
    id: int
    created_at: datetime | None = None
    last_updated: datetime | None = None


def load_dotenv_if_exists() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_postgres_config_from_compose() -> dict[str, Any]:
    compose_path = Path(__file__).resolve().parents[1] / "docker-compose.yml"

    service_name = "postgres"
    container_name = "postgres"
    user = os.getenv("POSTGRES_USER", "postgres")
    db_name = os.getenv("POSTGRES_DB", "postgres")
    host_port = 5432
    container_port = 5432

    if yaml is not None and compose_path.exists():
        compose = yaml.safe_load(compose_path.read_text(encoding="utf-8")) or {}
        services = compose.get("services", {})

        for key, service in services.items():
            image = str(service.get("image", ""))
            if "postgres" not in image.lower():
                continue

            service_name = key
            container_name = service.get("container_name", key)

            environment = service.get("environment", {}) or {}
            if isinstance(environment, dict):
                user = environment.get("POSTGRES_USER", user)
                db_name = environment.get("POSTGRES_DB", db_name)

            ports = service.get("ports", []) or []
            if ports:
                mapping = str(ports[0]).replace('"', "").replace("'", "")
                if ":" in mapping:
                    host_raw, container_raw = mapping.split(":", 1)
                    host_port = int(host_raw)
                    container_port = int(container_raw)
                else:
                    host_port = int(mapping)
                    container_port = int(mapping)
            break

    in_docker = Path("/.dockerenv").exists()
    default_host = service_name if in_docker else "localhost"
    default_port = container_port if in_docker else host_port

    return {
        "host": os.getenv("POSTGRES_HOST", default_host),
        "port": int(os.getenv("POSTGRES_PORT", str(default_port))),
        "dbname": os.getenv("POSTGRES_DB", db_name),
        "user": os.getenv("POSTGRES_USER", user),
        "password": os.getenv("POSTGRES_PASSWORD", ""),
        "container_name": container_name,
        "service_name": service_name,
    }


def get_db_connection():
    load_dotenv_if_exists()
    cfg = load_postgres_config_from_compose()
    return psycopg.connect(
        host=cfg["host"],
        port=cfg["port"],
        dbname=cfg["dbname"],
        user=cfg["user"],
        password=cfg["password"],
        row_factory=dict_row,
    )


@app.get("/doentes", response_model=list[DoenteOut])
def list_doentes() -> list[dict[str, Any]]:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, numero_processo, nome, data_nascimento, genero, morada,
                       codigo_postal, localidade, contacto_telefone, contacto_email,
                       observacoes, created_at, last_updated
                FROM doentes
                ORDER BY id ASC
                """
            )
            return list(cur.fetchall())


@app.get("/doentes/numero-processo/{numero_processo}", response_model=DoenteOut)
def get_doente_by_numero_processo(numero_processo: str) -> dict[str, Any]:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, numero_processo, nome, data_nascimento, genero, morada,
                       codigo_postal, localidade, contacto_telefone, contacto_email,
                       observacoes, created_at, last_updated
                FROM doentes
                WHERE numero_processo = %s
                """,
                (numero_processo,),
            )
            row = cur.fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Doente nao encontrado")
            return dict(row)


@app.get("/doentes/{doente_id}", response_model=DoenteOut)
def get_doente(doente_id: int) -> dict[str, Any]:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, numero_processo, nome, data_nascimento, genero, morada,
                       codigo_postal, localidade, contacto_telefone, contacto_email,
                       observacoes, created_at, last_updated
                FROM doentes
                WHERE id = %s
                """,
                (doente_id,),
            )
            row = cur.fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Doente nao encontrado")
            return dict(row)


@app.post("/doentes", response_model=DoenteOut, status_code=status.HTTP_201_CREATED)
def create_doente(payload: DoenteCreate) -> dict[str, Any]:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    INSERT INTO doentes (
                        numero_processo, nome, data_nascimento, genero, morada,
                        codigo_postal, localidade, contacto_telefone, contacto_email,
                        observacoes
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, numero_processo, nome, data_nascimento, genero, morada,
                              codigo_postal, localidade, contacto_telefone, contacto_email,
                              observacoes, created_at, last_updated
                    """,
                    (
                        payload.numero_processo,
                        payload.nome,
                        payload.data_nascimento,
                        payload.genero,
                        payload.morada,
                        payload.codigo_postal,
                        payload.localidade,
                        payload.contacto_telefone,
                        payload.contacto_email,
                        payload.observacoes,
                    ),
                )
            except psycopg.IntegrityError as exc:
                conn.rollback()
                raise HTTPException(status_code=409, detail=f"Conflito ao criar doente: {exc}")
            return dict(cur.fetchone())


@app.put("/doentes/{doente_id}", response_model=DoenteOut)
def replace_doente(doente_id: int, payload: DoenteUpdate) -> dict[str, Any]:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    UPDATE doentes
                    SET numero_processo = %s,
                        nome = %s,
                        data_nascimento = %s,
                        genero = %s,
                        morada = %s,
                        codigo_postal = %s,
                        localidade = %s,
                        contacto_telefone = %s,
                        contacto_email = %s,
                        observacoes = %s,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING id, numero_processo, nome, data_nascimento, genero, morada,
                              codigo_postal, localidade, contacto_telefone, contacto_email,
                              observacoes, created_at, last_updated
                    """,
                    (
                        payload.numero_processo,
                        payload.nome,
                        payload.data_nascimento,
                        payload.genero,
                        payload.morada,
                        payload.codigo_postal,
                        payload.localidade,
                        payload.contacto_telefone,
                        payload.contacto_email,
                        payload.observacoes,
                        doente_id,
                    ),
                )
            except psycopg.IntegrityError as exc:
                conn.rollback()
                raise HTTPException(status_code=409, detail=f"Conflito ao atualizar doente: {exc}")

            row = cur.fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Doente nao encontrado")
            return dict(row)


@app.patch("/doentes/{doente_id}", response_model=DoenteOut)
def patch_doente(doente_id: int, payload: DoentePatch) -> dict[str, Any]:
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="Nada para atualizar")

    set_parts: list[str] = []
    values: list[Any] = []
    for key, value in changes.items():
        set_parts.append(f"{key} = %s")
        values.append(value)

    set_parts.append("last_updated = CURRENT_TIMESTAMP")
    values.append(doente_id)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    f"""
                    UPDATE doentes
                    SET {', '.join(set_parts)}
                    WHERE id = %s
                    RETURNING id, numero_processo, nome, data_nascimento, genero, morada,
                              codigo_postal, localidade, contacto_telefone, contacto_email,
                              observacoes, created_at, last_updated
                    """,
                    tuple(values),
                )
            except psycopg.IntegrityError as exc:
                conn.rollback()
                raise HTTPException(status_code=409, detail=f"Conflito ao atualizar doente: {exc}")

            row = cur.fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Doente nao encontrado")
            return dict(row)


@app.delete("/doentes/{doente_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doente(doente_id: int) -> Response:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM doentes WHERE id = %s", (doente_id,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Doente nao encontrado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/config/db")
def db_runtime_config() -> dict[str, Any]:
    cfg = load_postgres_config_from_compose()
    return {
        "host": cfg["host"],
        "port": cfg["port"],
        "dbname": cfg["dbname"],
        "user": cfg["user"],
        "docker_postgres_service": cfg["service_name"],
        "docker_postgres_container": cfg["container_name"],
    }
