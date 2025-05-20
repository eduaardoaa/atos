import mysql.connector
import streamlit as st
import importlib
import sys
from pathlib import Path

def conexaobanco():
    try:
        conn = mysql.connector.connect(
            host="maglev.proxy.rlwy.net",
            port=10175,
            user="root",
            password="DrMCLnXdmCSDqBsJSiZzXmfaIxHvMkkL",
            database="railway"
        )
        return conn
    except mysql.connector.Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

def validacao(usr, passw):
    conn = conexaobanco()
    if not conn:
        return

    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT u.*, g.codigo as grupo_codigo 
    FROM usuarios u
    LEFT JOIN grupoempresa g ON u.grupo_id = g.id
    WHERE u.usuario = %s AND u.senha = %s
    """
    cursor.execute(query, (usr, passw))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        st.session_state.authenticated = True  
        st.session_state.user_info = {
            'id': user['id'],
            'nome': user['Nome'],
            'permissao': user['permissao'],
            'grupo_id': user.get('grupo_id'),
            'grupo_codigo': user.get('grupo_codigo', '')
        }
        st.success('Login feito com sucesso!')

        if user['permissao'] == 'adm':
            st.session_state.page = "adm"
            st.rerun()
        elif user['permissao'] == 'cliente':
            if user.get('grupo_codigo'):
                codigo_grupo = user['grupo_codigo'].lower().strip()
                
                # Verifica se o módulo existe antes de redirecionar
                module_path = f"pages.{codigo_grupo}"
                try:
                    importlib.import_module(module_path)
                    st.session_state.page = "dashboard"
                    st.session_state.dashboard_page = codigo_grupo
                    st.rerun()
                except ImportError:
                    st.error(f'Dashboard para o grupo {codigo_grupo} não está disponível.')
            else:
                st.error('Usuário não está associado a nenhum grupo válido.')
        else:
            st.error('Permissão desconhecida. Não foi possível redirecionar.')
    else:
        st.error('Usuário ou senha incorretos, tente novamente.')

def arealogin():
    st.set_page_config(page_title="Login", page_icon="🔒", layout="centered")
    
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        st.image("logoatos.png", width=150)

    with st.form('sign_in'):
        st.caption('Por favor, insira seu usuário e senha.')
        username = st.text_input('Usuário')
        password = st.text_input('Senha', type='password')

        botaoentrar = st.form_submit_button(label="Entrar", type="primary", use_container_width=True)

    if botaoentrar:
        validacao(username, password)

def carregar_pagina(nome_pagina):
    try:
        if nome_pagina == "dashboard":
            # Verifica se o módulo existe na pasta pages
            pagina = st.session_state.get('dashboard_page', 'atos')  # padrão para 'atos'
            module_path = f"pages.{pagina}"
            
            try:
                modulo = importlib.import_module(module_path)
                # Verifica se a função principal existe
                if hasattr(modulo, 'main'):
                    modulo.main()
                else:
                    st.error(f'O módulo {pagina} não possui uma função main()')
                    if st.button("Voltar"):
                        st.session_state.authenticated = False
                        st.session_state.page = None
                        st.rerun()
            except ImportError as e:
                st.error(f'Dashboard para este grupo não está disponível. Erro: {str(e)}')
                if st.button("Voltar"):
                    st.session_state.authenticated = False
                    st.session_state.page = None
                    st.rerun()
        elif nome_pagina == "adm":
            try:
                modulo = importlib.import_module("pages.adm")
                modulo.main()
            except ImportError:
                st.error('Módulo de administração não encontrado')
                if st.button("Voltar"):
                    st.session_state.authenticated = False
                    st.session_state.page = None
                    st.rerun()
        else:
            st.error('Página desconhecida')
            if st.button("Voltar"):
                st.session_state.authenticated = False
                st.session_state.page = None
                st.rerun()
    except Exception as e:
        st.error(f'Erro inesperado: {str(e)}')
        if st.button("Voltar"):
            st.session_state.authenticated = False
            st.session_state.page = None
            st.rerun()

def main():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        arealogin()
    else:
        if "page" in st.session_state:
            carregar_pagina(st.session_state.page)

if __name__ == "__main__":
    # Adiciona o diretório atual ao path para garantir que os imports funcionem
    sys.path.append(str(Path(__file__).parent))
    main()
