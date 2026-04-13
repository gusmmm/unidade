from pathlib import Path

import streamlit as st


def themes_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "themes"


def list_themes() -> list[str]:
    css_files = sorted(themes_dir().glob("*.css"))
    return [item.stem for item in css_files]


def apply_theme(theme_name: str) -> None:
    css_path = themes_dir() / f"{theme_name}.css"
    if not css_path.exists():
        st.warning(f"Tema '{theme_name}' nao encontrado em {themes_dir()}")
        return

    css = css_path.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
