from datetime import date

import requests
import streamlit as st

from shared.api import (
    create_doente,
    delete_doente,
    get_doente_by_numero_processo,
    list_doentes,
    patch_doente,
    serialize_doente_form,
    update_doente,
)
from shared.theme import apply_theme

st.set_page_config(page_title="Doentes", page_icon="[]", layout="wide")

if "theme_name" in st.session_state:
    apply_theme(st.session_state.theme_name)

st.title("Doentes")
st.caption("CRUD completo da tabela doentes via FastAPI")

if st.button("Atualizar lista", width="stretch"):
    st.rerun()

try:
    doentes = list_doentes()
except requests.RequestException as exc:
    st.error(f"Erro ao carregar doentes: {exc}")
    st.stop()

st.subheader("Lista")
st.dataframe(doentes, width="stretch", hide_index=True)

st.divider()

tab_create, tab_update, tab_patch, tab_delete, tab_search = st.tabs(
    ["Criar", "Atualizar", "Patch", "Apagar", "Pesquisar por numero_processo"]
)


def form_fields(prefix: str, base: dict | None = None) -> dict:
    if base is None:
        base = {}

    genero_options = ["", "M", "F", "Outro"]
    base_genero = base.get("genero") or ""
    genero_index = genero_options.index(base_genero) if base_genero in genero_options else 0

    data_default_raw = base.get("data_nascimento")
    if isinstance(data_default_raw, str):
        data_default = date.fromisoformat(data_default_raw)
    elif isinstance(data_default_raw, date):
        data_default = data_default_raw
    else:
        data_default = date(2000, 1, 1)

    numero_processo = st.text_input("Numero processo", value=base.get("numero_processo", ""), key=f"{prefix}_np")
    nome = st.text_input("Nome", value=base.get("nome", ""), key=f"{prefix}_nome")
    data_nascimento = st.date_input("Data nascimento", value=data_default, key=f"{prefix}_dn")
    genero = st.selectbox("Genero", options=genero_options, index=genero_index, key=f"{prefix}_gen")
    morada = st.text_input("Morada", value=base.get("morada", "") or "", key=f"{prefix}_morada")
    codigo_postal = st.text_input(
        "Codigo postal", value=base.get("codigo_postal", "") or "", key=f"{prefix}_cp"
    )
    localidade = st.text_input("Localidade", value=base.get("localidade", "") or "", key=f"{prefix}_loc")
    contacto_telefone = st.text_input(
        "Contacto telefone", value=base.get("contacto_telefone", "") or "", key=f"{prefix}_tel"
    )
    contacto_email = st.text_input(
        "Contacto email", value=base.get("contacto_email", "") or "", key=f"{prefix}_mail"
    )
    observacoes = st.text_area("Observacoes", value=base.get("observacoes", "") or "", key=f"{prefix}_obs")

    return serialize_doente_form(
        numero_processo=numero_processo,
        nome=nome,
        data_nascimento=data_nascimento,
        genero=genero,
        morada=morada,
        codigo_postal=codigo_postal,
        localidade=localidade,
        contacto_telefone=contacto_telefone,
        contacto_email=contacto_email,
        observacoes=observacoes,
    )


with tab_create:
    st.markdown("### Criar doente")
    with st.form("create_doente_form"):
        payload = form_fields("create")
        submitted = st.form_submit_button("Criar", width="stretch")
    if submitted:
        try:
            created = create_doente(payload)
            st.success(f"Doente criado com id {created['id']}")
        except requests.RequestException as exc:
            st.error(f"Erro ao criar: {exc}")


with tab_update:
    st.markdown("### Atualizar doente (PUT)")
    with st.form("update_doente_form"):
        doente_id = st.number_input("ID doente", min_value=1, step=1, value=1)
        payload = form_fields("update")
        submitted = st.form_submit_button("Atualizar", width="stretch")
    if submitted:
        try:
            updated = update_doente(int(doente_id), payload)
            st.success(f"Doente atualizado: {updated['id']}")
        except requests.RequestException as exc:
            st.error(f"Erro ao atualizar: {exc}")


with tab_patch:
    st.markdown("### Atualizacao parcial (PATCH)")
    st.caption("Preencha apenas os campos que quer mudar")
    with st.form("patch_doente_form"):
        doente_id_patch = st.number_input("ID doente", min_value=1, step=1, value=1, key="patch_id")

        numero_processo = st.text_input("Numero processo", key="patch_np")
        nome = st.text_input("Nome", key="patch_nome")
        data_nascimento = st.text_input("Data nascimento (YYYY-MM-DD)", key="patch_dn")
        genero = st.selectbox("Genero", options=["", "M", "F", "Outro"], key="patch_gen")
        morada = st.text_input("Morada", key="patch_morada")
        codigo_postal = st.text_input("Codigo postal", key="patch_cp")
        localidade = st.text_input("Localidade", key="patch_loc")
        contacto_telefone = st.text_input("Contacto telefone", key="patch_tel")
        contacto_email = st.text_input("Contacto email", key="patch_mail")
        observacoes = st.text_area("Observacoes", key="patch_obs")

        submitted_patch = st.form_submit_button("Aplicar patch", width="stretch")

    if submitted_patch:
        patch_payload: dict = {}
        if numero_processo.strip():
            patch_payload["numero_processo"] = numero_processo.strip()
        if nome.strip():
            patch_payload["nome"] = nome.strip()
        if data_nascimento.strip():
            patch_payload["data_nascimento"] = data_nascimento.strip()
        if genero:
            patch_payload["genero"] = genero
        if morada.strip():
            patch_payload["morada"] = morada.strip()
        if codigo_postal.strip():
            patch_payload["codigo_postal"] = codigo_postal.strip()
        if localidade.strip():
            patch_payload["localidade"] = localidade.strip()
        if contacto_telefone.strip():
            patch_payload["contacto_telefone"] = contacto_telefone.strip()
        if contacto_email.strip():
            patch_payload["contacto_email"] = contacto_email.strip()
        if observacoes.strip():
            patch_payload["observacoes"] = observacoes.strip()

        if not patch_payload:
            st.warning("Sem campos para atualizar")
        else:
            try:
                patched = patch_doente(int(doente_id_patch), patch_payload)
                st.success(f"Doente atualizado parcialmente: {patched['id']}")
            except requests.RequestException as exc:
                st.error(f"Erro no patch: {exc}")


with tab_delete:
    st.markdown("### Apagar doente")
    st.warning("Esta operacao remove o registo em definitivo")
    with st.form("delete_doente_form"):
        doente_id_delete = st.number_input("ID doente", min_value=1, step=1, value=1, key="delete_id")
        confirm_delete = st.checkbox("Confirmo que quero apagar")
        submitted_delete = st.form_submit_button("Apagar", width="stretch")

    if submitted_delete:
        if not confirm_delete:
            st.warning("Marque a confirmacao antes de apagar")
        else:
            try:
                delete_doente(int(doente_id_delete))
                st.success("Doente apagado")
            except requests.RequestException as exc:
                st.error(f"Erro ao apagar: {exc}")


with tab_search:
    st.markdown("### Pesquisar doente por numero_processo")
    with st.form("search_doente_np"):
        numero_processo_search = st.text_input("Numero processo")
        submitted_search = st.form_submit_button("Pesquisar", width="stretch")

    if submitted_search:
        if not numero_processo_search.strip():
            st.warning("Indique um numero_processo")
        else:
            try:
                doente = get_doente_by_numero_processo(numero_processo_search.strip())
                st.json(doente)
            except requests.RequestException as exc:
                st.error(f"Erro na pesquisa: {exc}")
