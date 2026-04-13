import os

import streamlit as st

from shared.theme import apply_theme, list_themes

st.set_page_config(page_title="Unidade", page_icon="+", layout="wide")

available_themes = list_themes()
if not available_themes:
    st.error("Nenhum tema encontrado. Adicione ficheiros .css em frontend/themes.")
    st.stop()

default_theme = "light_clean" if "light_clean" in available_themes else available_themes[0]

if "theme_name" not in st.session_state:
    st.session_state.theme_name = default_theme

if st.session_state.theme_name not in available_themes:
    st.session_state.theme_name = default_theme

header_left, header_mid, header_right = st.columns([3, 2, 2])

with header_left:
    st.title("Unidade")
    st.caption("Frontend Streamlit para gestao de doentes")

with header_mid:
    st.markdown("Tema")
    current_theme_index = available_themes.index(st.session_state.theme_name)
    if st.button("Mudar tema", width="stretch"):
        next_index = (current_theme_index + 1) % len(available_themes)
        st.session_state.theme_name = available_themes[next_index]
        st.rerun()

with header_right:
    st.markdown("Tema")
    selected_theme = st.selectbox(
        "Selecionar tema",
        options=available_themes,
        index=available_themes.index(st.session_state.theme_name),
        label_visibility="collapsed",
    )
    if selected_theme != st.session_state.theme_name:
        st.session_state.theme_name = selected_theme
        st.rerun()

apply_theme(st.session_state.theme_name)

st.markdown("### Inicio")
st.write("Use o menu lateral para abrir a pagina Doentes e executar operacoes CRUD.")

st.info(
    f"Backend URL atual: {os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')}"
)
