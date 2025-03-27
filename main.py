import mysql.connector
import streamlit as st
import logging

# Configuração do logger
logging.basicConfig(level=logging.DEBUG)

# Função para detectar se o dispositivo é móvel com JavaScript
def is_mobile():
    if "is_mobile" not in st.session_state:
        st.session_state.is_mobile = False
        st.markdown(
            """
            <script>
            if(window.innerWidth <= 800) {
                window.parent.postMessage({is_mobile: true}, "*");
            } else {
                window.parent.postMessage({is_mobile: false}, "*");
            }
            </script>
            """, unsafe_allow_html=True)
    
    return st.session_state.is_mobile

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

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

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
            st.rerun()  # Redireciona para a página de admin
        elif permissao == 'cliente':
            st.session_state.page = "dashboard"
            st.rerun()  # Redireciona para a página do cliente
        else:
            st.error('Permissão desconhecida. Não foi possível redirecionar.')

    else:
        st.error('Usuário ou senha incorretos, tente novamente.')

# Página principal de login
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

if st.session_state.authenticated:
    if "page" in st.session_state:
        if st.session_state.page == "adm":
            # Aqui começa a parte do admin que você pediu para adicionar
            import streamlit as st
            import mysql.connector

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

            def listarusuarios():
                usuarios = puxarusuarios()

                if is_mobile():
                    # Exibe os dados de forma mais compacta para dispositivos móveis
                    for user in usuarios:
                        st.subheader(f"ID: {user[0]}")
                        st.write(f"**Nome Empresa**: {user[1]}")
                        st.write(f"**Usuário**: {user[2]}")
                        st.write(f"**Senha**: {user[3]}")
                        st.write(f"**Número**: {user[4]}")
                        st.write(f"**Permissão**: {user[5]}")
                        st.markdown("---")
                else:
                    # Exibe os dados em formato de tabela para telas maiores
                    table_columns = [2, 10, 5, 5, 8, 4, 2, 2]
                    header = st.columns(table_columns)
                    headers = ["ID", "NomeEmpresa", "Usuário", "Senha", "Número", "Permissão", "Editar", "Excluir"]

                    for col, header_text in zip(header, headers):
                        with col:
                            st.write(f"**{header_text}**")

                    for user in usuarios:
                        with st.container():
                            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([2, 10, 5, 5, 8, 4, 2, 2])

                            col1.write(user[0])  # ID
                            col2.write(user[1])  # NomeEmpresa
                            col3.write(user[2])  # Usuário
                            col4.write(user[3])  # Senha
                            col5.write(user[4])  # Número
                            col6.write(user[5])  # Permissão

                            if col7.button("✏️", key=f"edit_{user[0]}"):
                                st.session_state.editar_usuario = user[0]
                                st.rerun()

                            if col8.button("🗑️", key=f"delete_{user[0]}"):
                                st.session_state.confirmarexclusao = user[0]
                                st.session_state.usuario_a_excluir = user[1]
                                st.session_state.exclusao_confirmada = False
                                st.rerun()

                    if "confirmarexclusao" in st.session_state and st.session_state.confirmarexclusao == user[0] and not st.session_state.exclusao_confirmada:
                        st.subheader(f"Você realmente deseja excluir o usuário {st.session_state.usuario_a_excluir}?")

                        col1, col2 = st.columns([1, 1])
                        with col1:
                            if st.button("Sim", key=f"sim_{user[0]}"):
                                excluirusuario(user[0])
                                st.session_state.exclusao_confirmada = True
                                st.session_state.confirmarexclusao = None
                                st.rerun()

                        with col2:
                            if st.button("Não", key=f"nao_{user[0]}"):
                                st.session_state.exclusao_confirmada = True
                                st.session_state.confirmarexclusao = None
                                st.rerun()

                        st.markdown("---")

            st.set_page_config(layout="wide")
            st.title("Gerenciamento de Usuários")

            col1, col2 = st.columns([1, 1])

            with col1:
                if st.button("Adicionar Novo Usuário"):
                    st.session_state.novousuario = True
                    st.rerun()

            with col2:
                if st.button("Dashboard"):
                    st.session_state.page = "dashboard"  # Redireciona para o dashboard
                    st.rerun()

            if "novousuario" in st.session_state and st.session_state.novousuario:
                formularionovousuario()

            listarusuarios()

            if "editar_usuario" in st.session_state and st.session_state.editar_usuario:
                usuario_editar = next(user for user in puxarusuarios() if user[0] == st.session_state.editar_usuario)
                formularioeditarusuario(usuario_editar)

        elif st.session_state.page == "dashboard":
            # Configuração da página do dashboard
            st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
            st.title("Dashboard de Usuários")
            st.write("Aqui você pode visualizar as informações dos usuários.")
            st.write("Em construção...")
