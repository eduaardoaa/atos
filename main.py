import mysql.connector
import streamlit as st
import logging

# Configuração do logger
logging.basicConfig(level=logging.DEBUG)

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

# Função para puxar os usuários
def puxarusuarios():
    conexao = conexaobanco()
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

# Página de administração
if st.session_state.page == "adm":
    st.set_page_config(layout="wide")
    st.title("Gerenciamento de Usuários")

    # Botões de navegação
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Adicionar Novo Usuário"):
            st.session_state.novousuario = True
            st.rerun()

    with col2:
        if st.button("Dashboard"):
            st.session_state.page = "dashboard"  # Redireciona para o dashboard
            st.rerun()

    # Formulário de novo usuário (se estiver ativo)
    if "novousuario" in st.session_state and st.session_state.novousuario:
        formularionovousuario()

    # Listar usuários em formato tabela
    usuarios = puxarusuarios()
    if usuarios:
        # Ajustando a exibição para celular, usando dataframe
        if st.sidebar.empty():  # Verifica se a barra lateral está vazia (provável que seja celular)
            st.subheader("Lista de Usuários")
            # Exibe uma tabela mais compacta para celular
            usuarios_df = pd.DataFrame(usuarios, columns=["ID", "NomeEmpresa", "Usuário", "Senha", "Número", "Permissão"])
            st.table(usuarios_df)
        else:
            # Exibição tradicional no desktop com colunas
            st.subheader("Lista de Usuários")
            table_columns = [2, 6, 5, 6, 4, 3, 4, 4]  # Ajuste das colunas para desktop
            header = st.columns(table_columns)
            headers = ["ID", "NomeEmpresa", "Usuário", "Senha", "Número", "Permissão", "Editar", "Excluir"]

            for col, header_text in zip(header, headers):
                with col:
                    st.write(f"**{header_text}**")

            for user in usuarios:
                with st.container():
                    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([2, 6, 5, 6, 4, 3, 4, 4])

                    col1.write(user[0])  # ID
                    col2.write(user[1])  # NomeEmpresa
                    col3.write(user[2])  # Usuário
                    col4.write(user[3])  # Senha
                    col5.write(user[4])  # Número
                    col6.write(user[5])  # Permissão

                    # Botões de ação (editar e excluir)
                    with col7:
                        if st.button("✏️", key=f"edit_{user[0]}"):
                            st.session_state.editar_usuario = user[0]
                            st.rerun()
                    with col8:
                        if st.button("🗑️", key=f"delete_{user[0]}"):
                            st.session_state.confirmarexclusao = user[0]
                            st.session_state.usuario_a_excluir = user[1]
                            st.session_state.exclusao_confirmada = False
                            st.rerun()

    # Confirmação de exclusão
    if "confirmarexclusao" in st.session_state and not st.session_state.exclusao_confirmada:
        st.subheader(f"Você realmente deseja excluir o usuário {st.session_state.usuario_a_excluir}?")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Sim"):
                excluirusuario(st.session_state.confirmarexclusao)
                st.session_state.exclusao_confirmada = True
                st.session_state.confirmarexclusao = None
                st.rerun()

        with col2:
            if st.button("Não"):
                st.session_state.exclusao_confirmada = True
                st.session_state.confirmarexclusao = None
                st.rerun()

    # Redirecionamento para o formulário de edição de usuário
    if "editar_usuario" in st.session_state and st.session_state.editar_usuario:
        usuario_editar = next(user for user in puxarusuarios() if user[0] == st.session_state.editar_usuario)
        formularioeditarusuario(usuario_editar)
