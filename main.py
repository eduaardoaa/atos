import streamlit as st
import mysql.connector
import logging

# Função de conexão com banco de dados (não alterada)
def conexaobanco():
    try:
        conn = mysql.connector.connect(
            host="crossover.proxy.rlwy.net",
            port=17025,
            user="root",
            password="nwiMDSsxmcmDXWChimBQOIswEFlTUMms",
            database="railway"
        )
        if conn.is_connected():
            logging.debug("Conexão bem-sucedida ao banco de dados")
        return conn
    except mysql.connector.Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função de validação (não alterada)
def validacao(usr, passw):
    conn = conexaobanco()
    if not conn:
        return

    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM usuarios WHERE usuario = %s AND senha = %s"
    try:
        cursor.execute(query, (usr, passw))
        user = cursor.fetchone()
    except mysql.connector.Error as e:
        st.error(f"Erro ao executar a consulta de validação: {e}")
        logging.error(f"Erro ao executar a consulta de validação: {e}")
        cursor.close()
        conn.close()
        return

    cursor.close()
    conn.close()

    if user:
        st.session_state.authenticated = True
        st.success('Login feito com sucesso!')

        permissao = user.get('permissao')
        if permissao == 'adm':
            st.session_state.page = "adm"
            st.rerun()
        elif permissao == 'cliente':
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error('Permissão desconhecida. Não foi possível redirecionar.')

    else:
        st.error('Usuário ou senha incorretos, tente novamente.')

# Página de login (não alterada)
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logoatos.png", width=150)

    with st.form('sign_in'):
        st.caption('Por favor, insira seu usuário e senha.')
        username = st.text_input('Usuário')
        password = st.text_input('Senha', type='password')

        botaoentrar = st.form_submit_button(label="Entrar", type="primary", use_container_width=True)

    if botaoentrar:
        validacao(username, password)

# Admin e Dashboard
if st.session_state.authenticated:
    if "page" in st.session_state:
        if st.session_state.page == "adm":
            # Função para conectar ao banco de dados
            def conectarbanco():
                try:
                    conn = mysql.connector.connect(
                        host="crossover.proxy.rlwy.net",
                        port=17025,
                        user="root",
                        password="nwiMDSsxmcmDXWChimBQOIswEFlTUMms",
                        database="railway"
                    )
                    return conn
                except mysql.connector.Error as e:
                    st.error(f"Erro ao conectar ao banco de dados: {e}")
                    logging.error(f"Erro ao conectar ao banco de dados: {e}")
                    return None

            # Função para puxar dados dos usuários
            def puxarusuarios():
                conexao = conectarbanco()
                if conexao:
                    cursor = conexao.cursor()
                    try:
                        cursor.execute("SELECT id, NomeEmpresa, usuario, senha, numero, permissao FROM usuarios ORDER BY id ASC")
                        usuarios = cursor.fetchall()
                    except mysql.connector.Error as e:
                        st.error(f"Erro ao executar a consulta para puxar usuários: {e}")
                        logging.error(f"Erro ao executar a consulta para puxar usuários: {e}")
                        return []
                    conexao.close()
                    return usuarios
                return []

            # Função para adicionar um novo usuário
            def novousuario(nome_empresa, usuario, senha, numero, permissao):
                conexao = conectarbanco()
                if conexao:
                    cursor = conexao.cursor()

                    try:
                        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = %s", (usuario,))
                        count_usuario = cursor.fetchone()[0]

                        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE numero = %s", (numero,))
                        count_numero = cursor.fetchone()[0]

                        if count_usuario > 0:
                            st.error("Nome de usuário já está sendo utilizado.")
                            return False

                        if count_numero > 0:
                            st.error("Número já está sendo utilizado.")
                            return False

                        cursor.execute(
                            "INSERT INTO usuarios (NomeEmpresa, usuario, senha, numero, permissao) VALUES (%s, %s, %s, %s, %s)",
                            (nome_empresa, usuario, senha, numero, permissao)
                        )
                        conexao.commit()
                    except mysql.connector.Error as e:
                        st.error(f"Erro ao adicionar novo usuário: {e}")
                        logging.error(f"Erro ao adicionar novo usuário: {e}")
                        conexao.rollback()
                        return False
                    conexao.close()
                    return True
                return False

            # Página de administração
            st.set_page_config(layout="wide")
            st.title("Gerenciamento de Usuários")

            col1, col2 = st.columns([1, 1])

            with col1:
                if st.button("Adicionar Novo Usuário", use_container_width=True):
                    st.session_state.novousuario = True
                    st.rerun()

            with col2:
                if st.button("Dashboard", use_container_width=True):
                    st.session_state.page = "dashboard"  # Redireciona para o dashboard
                    st.rerun()

            if "novousuario" in st.session_state and st.session_state.novousuario:
                formularionovousuario()

            listarusuarios()

        elif st.session_state.page == "dashboard":
            # Página do Dashboard
            st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
            st.title("Dashboard de Usuários")
            st.write("Aqui você pode visualizar as informações dos usuários.")
            st.write("Em construção...")
