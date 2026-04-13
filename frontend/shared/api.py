from datetime import date
import os

import requests


API_BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


def _url(path: str) -> str:
    return f"{API_BASE_URL}{path}"


def list_doentes() -> list[dict]:
    response = requests.get(_url("/doentes"), timeout=10)
    response.raise_for_status()
    return response.json()


def get_doente_by_numero_processo(numero_processo: str) -> dict:
    response = requests.get(_url(f"/doentes/numero-processo/{numero_processo}"), timeout=10)
    response.raise_for_status()
    return response.json()


def create_doente(payload: dict) -> dict:
    response = requests.post(_url("/doentes"), json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def update_doente(doente_id: int, payload: dict) -> dict:
    response = requests.put(_url(f"/doentes/{doente_id}"), json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def patch_doente(doente_id: int, payload: dict) -> dict:
    response = requests.patch(_url(f"/doentes/{doente_id}"), json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def delete_doente(doente_id: int) -> None:
    response = requests.delete(_url(f"/doentes/{doente_id}"), timeout=10)
    response.raise_for_status()


def serialize_doente_form(
    numero_processo: str,
    nome: str,
    data_nascimento: date,
    genero: str,
    morada: str,
    codigo_postal: str,
    localidade: str,
    contacto_telefone: str,
    contacto_email: str,
    observacoes: str,
) -> dict:
    return {
        "numero_processo": numero_processo.strip(),
        "nome": nome.strip(),
        "data_nascimento": data_nascimento.isoformat(),
        "genero": genero if genero else None,
        "morada": morada.strip() or None,
        "codigo_postal": codigo_postal.strip() or None,
        "localidade": localidade.strip() or None,
        "contacto_telefone": contacto_telefone.strip() or None,
        "contacto_email": contacto_email.strip() or None,
        "observacoes": observacoes.strip() or None,
    }
