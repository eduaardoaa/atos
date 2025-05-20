import streamlit as st
import importlib

# ✅ Esta deve ser a PRIMEIRA chamada do Streamlit
st.set_page_config(page_title="Atos Capital", page_icon="📊", layout="wide")


def arealogin():
    st.title("🔒 Área de Login")

    with st.form("login_form"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")

    if submit:
        # Lógica de autenticação simples para exemplo
        if usuario == "admin" and senha == "123":
            st.session_state.autenticado = True
            st.session_state.page = "paginaatos"
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha inválidos")


def carregar_pagina(pagina):
    try:
        modulo = importlib.import_module("atos.dashboard")  # ou baseado no nome da página
        getattr(modulo, pagina)()
    except Exception as e:
        st.error(f"Erro ao carregar a página '{pagina}': {e}")


def main():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if "page" not in st.session_state:
        arealogin()
    elif st.session_state.autenticado:
        carregar_pagina(st.session_state.page)
    else:
        arealogin()


if __name__ == "__main__":
    main()
