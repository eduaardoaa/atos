import streamlit as st
import mysql.connector

def conectarbanco():
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            user='root',
            password='sua_senha',
            database='atoscapital'
        )
        return conexao
    except mysql.connector.Error as err:
        st.error(f"Erro ao conectar ao banco de dados: {err}")
        return None

def puxarusuarios():
    conexao = conectarbanco()
    if conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT id, NomeEmpresa, usuario, senha, numero, permissao FROM usuarios ORDER BY id ASC")
        usuarios = cursor.fetchall()
        conexao.close()
        return usuarios
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

def excluirusuario(user_id):
    conexao = conectarbanco()
    if conexao:
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
        conexao.commit()
        conexao.close()
        st.success("Usuário excluído com sucesso!")
        st.rerun()

def formularionovousuario():
    col1, col2 = st.columns([9, 1])
    with col2:
        if st.button("❌ Fechar", key="fecharformulario"):
            st.session_state.novousuario = False
            st.rerun()

    st.subheader("Adicionar Novo Usuário")

    with st.form(key="formnovousuario"):
        nome_empresa = st.text_input("Nome/Empresa")
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
        nome_empresa = st.text_input("Nome/Empresa", value=user[1])
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
    headers = ["ID", "Nome/Empresa", "Usuário", "Senha", "Número", "Permissão", "Editar", "Excluir"]

    for col, header_text in zip(header, headers):
        with col:
            st.write(f"**{header_text}**")

    for user in usuarios:
        with st.container():
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([2, 10, 5, 5, 8, 4, 2, 2])
            col1.write(user[0])  # ID
            col2.write(user[1])  # Nome/Empresa
            col3.write(user[2])  # Usuário
            col4.write(user[3])  # Senha
            col5.write(user[4])  # Número
            col6.write(user[5])  # Permissão

            if col7.button("✏️", key=f"edit_{user[0]}"):
                st.session_state.editar_usuario = user[0]
                st.rerun()

            # Confirmar exclusão
            if col8.button("🗑️", key=f"delete_{user[0]}"):
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

# Página principal
def main():
    if "novousuario" not in st.session_state:
        st.session_state.novousuario = False
    if "editar_usuario" not in st.session_state:
        st.session_state.editar_usuario = None

    st.title("Gestão de Usuários")

    if st.session_state.novousuario:
        formularionovousuario()
    elif st.session_state.editar_usuario:
        user = next((user for user in puxarusuarios() if user[0] == st.session_state.editar_usuario), None)
        if user:
            formularioeditarusuario(user)
    else:
        listarusuarios()

if __name__ == "__main__":
    main()
