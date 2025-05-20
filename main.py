import streamlit as st
import importlib
import mysql.connector

# ✅ Configuração da página deve ser a primeira coisa a ser chamada
st.set_page_config(page_title="Atos Capital", page_icon="📊", layout="wide")


# ✅ Conexão com o banco de dados
def conectar_bd():
    return mysql.connector.connect(
        host="bancoteste.mysql.database.azure.com",
        user="eduaardoaa",
        password="Atos@123",
        database="atos"
    )


# ✅ Área de login
def arealogin():
    st.title("🔒 Área de Login")

    with st.form("login_form"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")

    if submit:
        conexao = conectar_bd()
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s AND senha = %s", (usuario, senha))
        resultado = cursor.fetchone()

        if resultado:
            st.session_state.autenticado = True
            st.session_state.page = resultado[3]  # coluna com nome da página
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha inválidos")

        cursor.close()
        conexao.close()


# ✅ Carrega o módulo dinamicamente com base no nome da página
def carregar_pagina(pagina):
    try:
        modulo = importlib.import_module(f"atos.{pagina}")
        getattr(modulo, pagina)()
    except Exception as e:
        st.error(f"Erro ao carregar a página '{pagina}': {e}")


# ✅ Função principal
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
