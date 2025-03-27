import mysql.connector
import streamlit as st

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
            st.success("Conexão bem-sucedida!")
        return conn
    except mysql.connector.Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def validacao(usr, passw):
    conn = conexaobanco()
    if not conn:
        return

    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM usuarios WHERE usuario = %s AND senha = %s"
    cursor.execute(query, (usr, passw))
    user = cursor.fetchone()

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
                    if conn.is_connected():
                        st.success("Conexão bem-sucedida!")
                    return conn
                except mysql.connector.Error as e:
                    st.error(f"Erro ao conectar ao banco de dados: {e}")
                    return None

            def puxarusuarios():
                conexao = conectarbanco()
                if conexao:
                    cursor = conexao.cursor()
                    try:
                        cursor.execute("SELECT id, NomeEmpresa, usuario, senha, numero, permissao FROM usuarios ORDER BY id ASC")
                        usuarios = cursor.fetchall()
                        st.write(usuarios)  # Exibe os resultados para depuração
                        return usuarios
                    except mysql.connector.Error as e:
                        st.error(f"Erro ao executar consulta: {e}")
                        return []
                    finally:
                        cursor.close()
                        conexao.close()
                return []

            def atualizacaousuarios(user_id, nome_empresa, usuario, senha, numero, permissao):
                conexao = conectarbanco()
                if conexao:
                    cursor = conexao.cursor()

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
                    conexao.close()
                    return True
                return False

            def excluirusuario(user_id):
                conexao = conectarbanco()
                if conexao:
                    cursor = conexao.cursor()
                    cursor.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
                    conexao.commit()
                    conexao.close()
                    st.success("Usuário excluído com sucesso!")

            def novousuario(nome_empresa, usuario, senha, numero, permissao):
                conexao = conectarbanco()
                if conexao:
                    cursor = conexao.cursor()

                    # Verifica se o nome de usuário já existe
                    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = %s", (usuario,))
                    count_usuario = cursor.fetchone()[0]

                    # Verifica se o número já existe
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
                        with col7:
                            if st.button("✏️", key=f"editar{user[0]}"):
                                st.session_state.editar_usuario = user
                                st.rerun()

                        with col8:
                            if st.button("❌", key=f"excluir{user[0]}"):
                                excluirusuario(user[0])
                                st.session_state.editar_usuario = None
                                st.rerun()

            if "editar_usuario" in st.session_state and st.session_state.editar_usuario:
                formularioeditarusuario(st.session_state.editar_usuario)

            elif st.session_state.get("novousuario"):
                formularionovousuario()
            else:
                listarusuarios()
