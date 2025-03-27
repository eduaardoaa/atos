import mysql.connector
import streamlit as st
import logging

# Configuração do logger
logging.basicConfig(level=logging.DEBUG)

# Função de conexão com banco de dados
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

# Página principal de login
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

# Página de Admin e Dashboard
if st.session_state.authenticated:
    if "page" in st.session_state:
        if st.session_state.page == "adm":
            # Funções de conexão e manipulação do banco de dados
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

            def atualizacaousuarios(user_id, nome_empresa, usuario, senha, numero, permissao):
                conexao = conectarbanco()
                if conexao:
                    cursor = conexao.cursor()

                    try:
                        cursor.execute("SELECT id FROM usuarios WHERE usuario = %s", (usuario,))
                        usuario_existente = cursor.fetchone()

                        cursor.execute("SELECT id FROM usuarios WHERE numero = %s", (numero,))
                        numero_existente = cursor.fetchone()

                        if usuario_existente and usuario_existente[0] != user_id:
                            st.error("Nome de usuário já está sendo utilizado por outro usuário.")
                            return False

                        if numero_existente and numero_existente[0] != user_id:
                            st.error("Número já está sendo utilizado por outro usuário.")
                            return False

                        cursor.execute(
                            "UPDATE usuarios SET NomeEmpresa = %s, usuario = %s, senha = %s, numero = %s, permissao = %s WHERE id = %s",
                            (nome_empresa, usuario, senha, numero, permissao, user_id)
                        )
                        conexao.commit()
                    except mysql.connector.Error as e:
                        st.error(f"Erro ao atualizar o usuário: {e}")
                        logging.error(f"Erro ao atualizar o usuário: {e}")
                        conexao.rollback()
                        return False
                    conexao.close()
                    return True
                return False

            def excluirusuario(user_id):
                conexao = conectarbanco()
                if conexao:
                    cursor = conexao.cursor()
                    try:
                        cursor.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
                        conexao.commit()
                        st.success("Usuário excluído com sucesso!")
                    except mysql.connector.Error as e:
                        st.error(f"Erro ao excluir o usuário: {e}")
                        logging.error(f"Erro ao excluir o usuário: {e}")
                    conexao.close()

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

            def formularionovousuario():
                col1, col2 = st.columns([9, 1])
                with col2:
                    if st.button("❌ Fechar", key="fecharformulario"):
                        st.session_state.novousuario = False
                        st.rerun()

                st.subheader("Adicionar Novo Usuário")

                with st.form(key="formnovousuario"):
                    nome_empresa = st.text_input("NomeEmpresa")
                    usuario = st.text_input("Usuário")
                    senha = st.text_input("Senha", type="password")
                    numero = st.text_input("Número")
                    permissao = st.radio("Permissão", ["adm", "cliente"])

                    submit_button = st.form_submit_button(label="Adicionar Usuário")

                    if submit_button:
                        if novousuario(nome_empresa, usuario, senha, numero, permissao):
                            st.session_state.mensagem = "Novo usuário cadastrado com sucesso!"
                            st.session_state.novousuario = False
                            st.rerun()

            def formularioeditarusuario(user):
                col1, col2 = st.columns([9, 1])
                with col2:
                    if st.button("❌ Fechar", key=f"fecharformularioeditar{user[0]}"):
                        st.session_state.editar_usuario = None
                        st.rerun()

                st.subheader(f"Editar Usuário: {user[1]}")

                with st.form(key=f"editarusuario{user[0]}"):
                    nome_empresa = st.text_input("NomeEmpresa", value=user[1])
                    usuario = st.text_input("Usuário", value=user[2])
                    senha = st.text_input("Senha", value=user[3], type="password")
                    numero = st.text_input("Número", value=user[4])
                    permissao = st.radio("Permissão", ["adm", "cliente"], index=0 if user[5] == "adm" else 1)
                    submit_button = st.form_submit_button(label="Atualizar Usuário")

                    if submit_button:
                        if atualizacaousuarios(user[0], nome_empresa, usuario, senha, numero, permissao):
                            st.session_state.editar_usuario = None
                            st.rerun()

            def listarusuarios():
                usuarios = puxarusuarios()

                # Detectar se a largura da tela é pequena (típico de celular)
                is_mobile = st.experimental_get_query_params().get('device', ['desktop'])[0] == 'mobile'

                # Se for celular, exibe as informações detalhadas
                if is_mobile:
                    for user in usuarios:
                        st.markdown(f"### Usuário {user[0]}")
                        st.write(f"**Nome da Empresa:** {user[1]}")
                        st.write(f"**Usuário:** {user[2]}")
                        st.write(f"**Senha:** {user[3]}")
                        st.write(f"**Número:** {user[4]}")
                        st.write(f"**Permissão:** {user[5]}")

                        col1, col2 = st.columns([1, 1])
                        with col1:
                            if st.button(f"Editar {user[0]}", key=f"edit_{user[0]}"):
                                st.session_state.editar_usuario = user[0]
                                st.rerun()
                        
                        with col2:
                            if st.button(f"Excluir {user[0]}", key=f"delete_{user[0]}"):
                                st.session_state.confirmarexclusao = user[0]
                                st.session_state.usuario_a_excluir = user[1]
                                st.session_state.exclusao_confirmada = False
                                st.rerun()

                        # Exibir a confirmação para excluir o usuário
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

                # Caso contrário (para desktop), exibe a tabela padrão
                else:
                    # Exibição da tabela padrão
                    for user in usuarios:
                        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
                        with col1:
                            st.write(user[1])  # Nome da Empresa
                        with col2:
                            st.write(user[2])  # Usuário
                        with col3:
                            st.write(user[3])  # Senha
                        with col4:
                            st.write(user[4])  # Número
                        with col5:
                            st.write(user[5])  # Permissão

                        col1, col2 = st.columns([1, 1])
                        with col1:
                            if st.button(f"Editar {user[0]}", key=f"edit_{user[0]}"):
                                st.session_state.editar_usuario = user[0]
                                st.rerun()

                        with col2:
                            if st.button(f"Excluir {user[0]}", key=f"delete_{user[0]}"):
                                st.session_state.confirmarexclusao = user[0]
                                st.session_state.usuario_a_excluir = user[1]
                                st.session_state.exclusao_confirmada = False
                                st.rerun()

                        # Exibir a confirmação para excluir o usuário
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

            # Ajustes para visualização em dispositivos móveis
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

            if "editar_usuario" in st.session_state and st.session_state.editar_usuario:
                usuario_editar = next(user for user in puxarusuarios() if user[0] == st.session_state.editar_usuario)
                formularioeditarusuario(usuario_editar)

        elif st.session_state.page == "dashboard":
            # Página do Dashboard
            st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
            st.title("Dashboard de Usuários")
            st.write("Aqui você pode visualizar as informações dos usuários.")
            st.write("Em construção...")
