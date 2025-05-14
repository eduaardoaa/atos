from decimal import Decimal
import numpy as np
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import locale as lc
import consultaSQL
import sys
from inspect import getmembers, isfunction
from decimal import Decimal
import numpy as np
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import locale as lc
import consultaSQL
from datetime import datetime, timedelta

lc.setlocale(lc.LC_ALL, 'pt_BR')

def verificar_autenticacao():
    """Verifica se o usuário está autenticado"""
    if not st.session_state.get('authenticated', False):
        st.error("Você precisa fazer login para acessar esta página!")
        st.session_state.page = None
        st.rerun()

def pagina_nao_encontrada():
    """Página exibida quando não encontra a função correspondente"""
    verificar_autenticacao()
    st.error("🚨 Dashboard não configurado para este grupo")
    st.write(f"Grupo: {st.session_state.get('dashboard_page', 'Não especificado').replace('pagina', '')}")
    
    if st.button("↩️ Voltar"):
        st.session_state.page = None  
        st.switch_page("main.py")  

# PÁGINA ATOS


def paginaatos():
    verificar_autenticacao()

    # Configuração da página
    st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

    # Barra lateral
    if 'user_info' in st.session_state:
        # Adicionar botão Voltar apenas para administradores
        if st.session_state.user_info['permissao'].lower() == 'adm':
            if st.sidebar.button("⬅️ Voltar para Administração"):
                st.session_state.page = 'adm'
                st.rerun()

    # Inicializa a variável de sessão se não existir
    if 'pagina' not in st.session_state:
        st.session_state['pagina'] = 'principal'

    # Mostra a página apropriada com base no estado
    if st.session_state['pagina'] == 'principal':
        pagina_principal()
    else:
        pagina_mes_anterior()

    # Botão sair da conta (movido para depois das funções de página)
    if st.sidebar.button("🚪 Sair"):
        st.session_state.authenticated = False
        st.session_state.page = None
        st.rerun()

def pagina_principal():
    #inicio sidebar
    st.markdown(
    """ <style>
    [data-testid="stSidebar"] {
    background-color: #800000;
    } </style>
    """,
    unsafe_allow_html=True,
    )

    st.sidebar.header("Filtros")
    filiais = consultaSQL.obter_nmfilial()
    filial_selecionada = st.sidebar.selectbox("Selecione a Filial", filiais)

    if st.sidebar.button("Selecionar Meses Anteriores"):
        st.session_state['pagina'] = 'mes_anterior'
        st.rerun()

    mes_referencia = [datetime.now().strftime('%B').capitalize()]
    #fim sidebar

    #inicio cabeçalho
    left_co, cent_co, last_co = st.columns(3)
    with cent_co:
        st.image('logoatos.png', width=500)
    st.write(f"# Relatório de venda da {filial_selecionada}")
    #fim cabeçalho

    total_vendas = consultaSQL.obter_vendas_ano_anterior(filial_selecionada)
    meta_mes = consultaSQL.obter_meta_mes(filial_selecionada)
    previsao = consultaSQL.obter_previsao_vendas(filial_selecionada)
    acumulo_vendas_ano_anterior = consultaSQL.acumulo_vendas_periodo_ano_anterior(filial_selecionada)
    acumulo_meta_ano_anterior = consultaSQL.obter_acumulo_meta_ano_anterior(filial_selecionada)
    acumulo_de_vendas = consultaSQL.obter_acumulo_de_vendas(filial_selecionada)
    vendas_dia_anterior, data_venda_dia = consultaSQL.obter_ultima_venda_com_valor(filial_selecionada)
    percentual_crescimento_atual = consultaSQL.obter_percentual_de_crescimento_atual(filial_selecionada)
    percentual_crescimento_meta = consultaSQL.obter_percentual_crescimento_meta(filial_selecionada)
    vendas_mensais = consultaSQL.obter_vendas_anual_e_filial(filial_selecionada)

    @st.cache_data
    def grafico_de_barras(meta_mes, previsao, acumulo_meta_ano_anterior, acumulo_de_vendas):
        def safe_float(value):
            if value is None:
                return 0.0
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0.0

        meta_mes = safe_float(meta_mes)
        previsao = safe_float(previsao)
        acumulo_meta_ano_anterior = safe_float(acumulo_meta_ano_anterior)
        acumulo_de_vendas = safe_float(acumulo_de_vendas)

        categorias = ["Meta do mês", "Previsão", "Acumulado meta", "Acumulado Vendas"]
        valores = [meta_mes, previsao, acumulo_meta_ano_anterior, acumulo_de_vendas]
        cores = ["darkgray", "darkblue", "darkred", "white"]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=categorias,
            y=valores,
            marker_color=cores,
            text=[f"R$ {lc.currency(v, grouping=True, symbol=False)}" for v in valores],
            textposition='outside'
        ))

        fig.update_layout(
            title=f"📊 Metas e previsões da {filial_selecionada}",
            xaxis_title="",
            yaxis_title="Valor (R$)",
            font=dict(color="white", size=14),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=550,
            width=500,
            yaxis=dict(
                tickprefix="R$ ",
                separatethousands=True,
                tickformat=",."
            )
        )
        return fig

    @st.cache_data 
    def grafico_de_crescimento(percentual_crescimento_atual, percentual_crescimento_meta):
        try:
            percentual_crescimento_atual = float(percentual_crescimento_atual)
        except (ValueError, TypeError):
            percentual_crescimento_atual = 0.0

        try:
            percentual_crescimento_meta = float(percentual_crescimento_meta)
        except (ValueError, TypeError):
            percentual_crescimento_meta = 0.0
            
        fig = go.Figure()

        categorias = ["Cresc. 2025", "Cresc. meta"]
        valores = [percentual_crescimento_atual, percentual_crescimento_meta]
        cores = ["green","aqua"]

        fig.add_trace(go.Bar(
            x=categorias,
            y=valores,
            marker_color=cores,
            text=[f"{v:,.2f} %" for v in valores],
            textposition='outside'
        ))

        fig.update_layout(
            title= f"% Crescimento",
            xaxis_title="",
            yaxis_title="Valor %",
            font=dict(color="white", size=14),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=500, 
            width=500
        )
        return fig

    @st.cache_data
    def grafico_linhas_por_filial(mes_referencia, filial_selecionada):
        ano_atual = datetime.now().year
        vendas = consultaSQL.obter_vendas_por_mes_e_filial(mes_referencia, filial_selecionada, ano_atual)

        if not vendas:
            st.warning("Nenhuma venda encontrada para os filtros selecionados.")
            return None

        valores = [float(v[0]) if isinstance(v[0], Decimal) else v[0] for v in vendas]
        datas = [v[1] for v in vendas]
        meses = [v[2] for v in vendas]
        anos = [v[3] for v in vendas]

        df_vendas = pd.DataFrame({
            "Data": pd.to_datetime(datas),
            "Valor": valores,
            "Mês": [str(m) for m in meses],
            "Ano": [str(a) for a in anos]
        })

        df_vendas["Dia"] = df_vendas["Data"].dt.day 
        df_vendas["Valor_formatado"] = df_vendas["Valor"].apply(lambda x: lc.currency(x, grouping=True))
        df_vendas["MesAno"] = df_vendas["Mês"] + "/" + df_vendas["Ano"]

        fig = go.Figure()

        for mesano in df_vendas["MesAno"].unique():
            df_mesano = df_vendas[df_vendas["MesAno"] == mesano]

            fig.add_trace(go.Scatter(
                x=df_mesano["Dia"], 
                y=df_mesano["Valor"],
                mode='lines+markers',
                name=mesano,
                hovertemplate='Dia %{x}<br>Valor: %{customdata}<extra></extra>',
                customdata=df_mesano["Valor_formatado"]
            ))

        fig.update_layout(
            title=f"📈 Vendas comparadas {mes_referencia[0]} - {filial_selecionada}",
            xaxis_title="Dia do Mês",
            yaxis_title="Vendas (R$)",
            template="plotly_white",
            yaxis=dict(
                tickprefix="R$ ",
                separatethousands=True, 
                tickformat=",."
            )
        )
        return fig

    def grafico_de_evolucao_vendas(vendas_mensais):
        df_vendas = pd.DataFrame(list(vendas_mensais.items()), columns=['Mês', 'Vendas'])
        df_vendas['Mês'] = pd.to_datetime(df_vendas['Mês'], format='%m/%Y')
        df_vendas = df_vendas.sort_values("Mês")

        fig = go.Figure()

        df_vendas["Valor_formatado"] = df_vendas["Vendas"].apply(lambda y: lc.currency(y, grouping=True))

        fig.add_trace(go.Scatter(
            x=df_vendas["Mês"].dt.strftime('%m/%Y'),
            y=df_vendas["Vendas"],
            mode='lines+markers',
            name="Vendas",
            hovertemplate='Mês %{x}<br>Valor: %{customdata}<extra></extra>',
            customdata=df_vendas["Valor_formatado"]
        ))

        fig.update_layout(
            title=f"📊 Vendas nos últimos 12 meses - {filial_selecionada}",
            xaxis_title="Meses",
            yaxis_title="Valor das Vendas (R$)",
            font=dict(color="white", size=14),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis_tickformat="R$ ,.2f",
            template="plotly_white",
            yaxis=dict(
                tickprefix="R$ ",
                separatethousands=True,
                tickformat=",." 
            )
        )
        return fig

    # Mapa das filiais
    coordenadas_filiais = {
        'FILIAL BELÉM': {'latitude': -1.455, 'longitude': -48.489},
        'FILIAL BELO HORIZONTE': {'latitude': -19.9167, 'longitude': -43.9345},
        'FILIAL BRASÍLIA': {'latitude': -15.7939, 'longitude': -47.8828},
        'FILIAL CAMPINAS': {'latitude': -22.9056, 'longitude': -47.0608},
        'FILIAL CURITIBA': {'latitude': -25.4284, 'longitude': -49.2733},
        'FILIAL DUQUE DE CAXIAS': {'latitude': -22.7868, 'longitude': -43.3054},
        'FILIAL FORTALEZA': {'latitude': -3.7172, 'longitude': -38.5433},
        'FILIAL GOIÂNIA': {'latitude': -16.6869, 'longitude': -49.2648},
        'FILIAL GUARULHOS': {'latitude': -23.4545, 'longitude': -46.5333},
        'FILIAL MACEIÓ': {'latitude': -9.6658, 'longitude': -35.735},
        'FILIAL MANAUS': {'latitude': -3.119, 'longitude': -60.0217},
        'FILIAL RECIFE': {'latitude': -8.0476, 'longitude': -34.877},
        'FILIAL RIO DE JANEIRO': {'latitude': -22.9068, 'longitude': -43.1729},
        'FILIAL SALVADOR': {'latitude': -12.9714, 'longitude': -38.5014},
        'FILIAL SÃO GONÇALO': {'latitude': -22.8268, 'longitude': -43.0634},
        'FILIAL SÃO LUÍS': {'latitude': -2.5307, 'longitude': -44.3068},
        'FILIAL SÃO PAULO': {'latitude': -23.5505, 'longitude': -46.6333},
    }
    dados_vendas = pd.DataFrame({
        'filial': ['FILIAL BELÉM', 'FILIAL BELO HORIZONTE', 'FILIAL BRASÍLIA', 'FILIAL CAMPINAS', 
                  'FILIAL CURITIBA', 'FILIAL DUQUE DE CAXIAS', 'FILIAL FORTALEZA', 'FILIAL GOIÂNIA',
                  'FILIAL GUARULHOS', 'FILIAL MACEIÓ', 'FILIAL MANAUS', 'FILIAL RECIFE',
                  'FILIAL RIO DE JANEIRO', 'FILIAL SALVADOR', 'FILIAL SÃO GONÇALO', 
                  'FILIAL SÃO LUÍS', 'FILIAL SÃO PAULO']
    })
    dados_vendas['latitude'] = dados_vendas['filial'].map(lambda x: coordenadas_filiais[x]['latitude'])
    dados_vendas['longitude'] = dados_vendas['filial'].map(lambda x: coordenadas_filiais[x]['longitude'])

    # Exibição:
    col1, col2, col3 = st.columns(3)

    with col1:
       st.write(f"""#### Vendas 2024: \n 
                R$ {lc.currency(total_vendas, grouping=True, symbol=False)}
                """)
    with col2:
       st.write(f"""#### Acumulado 2024: \n
                R$ {lc.currency(acumulo_vendas_ano_anterior, grouping=True, symbol=False)}
                """)
    with col3:
       st.write(f"""#### Vendas do dia: ({data_venda_dia.strftime('%d/%m/%Y') if data_venda_dia else 'Sem data'})\n
                R$ {lc.currency(vendas_dia_anterior, grouping=True, symbol=False)} """)

    exibindo_grafico_de_barras = grafico_de_barras(meta_mes, previsao, acumulo_meta_ano_anterior, acumulo_de_vendas)
    st.plotly_chart(exibindo_grafico_de_barras, use_container_width=True)

    st.divider()

    exibindo_grafico_de_crescimento = grafico_de_crescimento(percentual_crescimento_atual, percentual_crescimento_meta)
    st.sidebar.plotly_chart(exibindo_grafico_de_crescimento)

    exibindo_grafico_de_linhas_vendas_por_mes = grafico_linhas_por_filial(mes_referencia, filial_selecionada)
    if exibindo_grafico_de_linhas_vendas_por_mes is not None:
        st.write(exibindo_grafico_de_linhas_vendas_por_mes)

    exibindo_grafico_acompanhamanto_anual = grafico_de_evolucao_vendas(vendas_mensais)
    st.write(exibindo_grafico_acompanhamanto_anual)

    dados_vendas["vendas"] = dados_vendas["filial"].apply(
        lambda f: max(float(consultaSQL.obter_acumulo_de_vendas(f) or 0), 1)
    )

    dados_vendas["vendas_formatado"] = dados_vendas["vendas"].apply(
        lambda v: f"R$ {lc.format_string('%.2f', v, grouping=True)}"
    )

    fig_mapa = px.scatter_mapbox(
        dados_vendas,
        lat="latitude",
        lon="longitude",
        color="vendas",
        size="vendas",
        size_max=30,
        zoom=3,
        height=600,
        color_continuous_scale="RdBu",
        custom_data=["filial", "vendas_formatado"]  
    )

    fig_mapa.update_traces(
        hovertemplate="<b>%{customdata[0]}</b><br>Vendas: %{customdata[1]}<extra></extra>"
    )

    fig_mapa.update_layout(
        mapbox_style="carto-darkmatter",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
        title="Vendas (R$)",
        tickvals=np.linspace(dados_vendas["vendas"].min(), dados_vendas["vendas"].max(), 5),
        ticktext=[f"R$ {lc.format_string('%.2f', v, grouping=True)}" for v in np.linspace(dados_vendas["vendas"].min(), dados_vendas["vendas"].max(), 5)]
        )
    )

    st.subheader("📍 Mapa das filiais com Vendas Acumuladas")
    st.plotly_chart(fig_mapa, use_container_width=True)

def pagina_mes_anterior():
    #inicio sidebar
    st.markdown(
    """ <style>
    [data-testid="stSidebar"] {
    background-color: #800000;
    } </style>
    """,
    unsafe_allow_html=True,
    )

    st.sidebar.header("Filtros")
    filiais = consultaSQL.obter_nmfilial()
    filial_selecionada = st.sidebar.selectbox("Selecione a Filial", filiais)

    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

    hoje = datetime.today()
    dia_hoje = hoje.day
    mes_atual = hoje.month
    ano_atual = hoje.year

    anos_disponiveis = consultaSQL.obter_anos_disponiveis()
    ano_selecionado = st.sidebar.selectbox("Selecione o ano de referência", anos_disponiveis, index=len(anos_disponiveis) - 1)

    if dia_hoje == 1 and mes_atual == 1:
        anos_disponiveis.remove(ano_atual)

    if ano_selecionado == ano_atual:
        if dia_hoje == 1:
            if mes_atual == 1:
                meses_disponiveis = []
            else:
                meses_disponiveis = meses[:mes_atual - 2]
        else:
            meses_disponiveis = meses[:mes_atual - 1]
    else:
        meses_disponiveis = meses

    if meses_disponiveis:
        mes_referencia = st.sidebar.selectbox("Selecione o mês de referência", meses_disponiveis)
        
        if st.sidebar.button("Voltar para mês atual"):
            st.session_state['pagina'] = 'principal'
            st.rerun()
    else:
        st.sidebar.warning("Nenhum mês disponível para seleção com base na data atual.")
        mes_referencia = None
          
    if mes_referencia:
        indice_mes_referencia = meses.index(mes_referencia) + 1

        if dia_hoje == 1 and indice_mes_referencia == mes_atual and ano_selecionado == ano_atual:
            data_ref = (hoje.replace(day=1) - timedelta(days=1)).replace(day=1)
            data_ref = (data_ref - timedelta(days=1)).replace(day=1)
            mes_final = data_ref.month
            ano_final = data_ref.year 
        elif dia_hoje != 1 and indice_mes_referencia == mes_atual and ano_selecionado == ano_atual:
            data_ref = (hoje.replace(day=1) - timedelta(days=1)).replace(day=1)
            mes_final = data_ref.month
            ano_final = data_ref.year
        else:
            mes_final = indice_mes_referencia
            ano_final = ano_selecionado

        mes_referencia = [mes_referencia]
        mes_selecionado = mes_referencia[0]
    #fim sidebar

    #inicio cabeçalho
    left_co, cent_co, last_co = st.columns(3)
    with cent_co:
        st.image('logoatos.png', width=500)
    st.write(f"# Relatório de venda da {filial_selecionada}")
    #fim cabeçalho

    if mes_referencia:
        total_vendas = consultaSQL.obter_vendas_ano_anterior_mes_anterior(filial_selecionada, mes_final, ano_final - 1)
        meta_mes = consultaSQL.obter_meta_mes_anterior(filial_selecionada, mes_final, ano_final)
        vendas_mes_atual = consultaSQL.obter_vendas_mes_anterior(filial_selecionada, mes_final, ano_selecionado)
        percentual_crescimento_atual = consultaSQL.obter_percentual_de_crescimento_atual(filial_selecionada)
        percentual_crescimento_meta = consultaSQL.obter_percentual_crescimento_meta(filial_selecionada)
        vendas_mensais = consultaSQL.obter_vendas_anual_e_filial(filial_selecionada)

        @st.cache_data
        def grafico_de_barras_mes_anterior(meta_mes, vendas_ano, vendas_mes_atual):
            def safe_float(value):
                if value is None:
                    return 0.0
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return 0.0

            meta_mes = safe_float(meta_mes)
            vendas_ano = safe_float(vendas_ano)
            vendas_mes_atual = safe_float(vendas_mes_atual)

            categorias = ["Meta do mês", f"Vendas ano anterior", f"Vendas de {mes_selecionado}"]
            valores = [meta_mes, vendas_ano, vendas_mes_atual]
            cores = ["darkgray", "darkblue", "darkred"]

            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=categorias,
                y=valores,
                marker_color=cores,
                text=[f"R$ {lc.currency(v, grouping=True, symbol=False)}" for v in valores],
                textposition='outside'
            ))

            fig.update_layout(
                title=f"📊 Mês: {mes_selecionado}",
                xaxis_title="",
                yaxis_title="Valor (R$)",
                font=dict(color="white", size=14),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                height=550,
                width=500,
                yaxis=dict(
                    tickprefix="R$ ",
                    separatethousands=True,
                    tickformat=",."
                )
            )
            return fig

        @st.cache_data 
        def grafico_de_crescimento_mes(percentual_crescimento_atual, percentual_crescimento_meta):
            try:
                percentual_crescimento_atual = float(percentual_crescimento_atual)
            except (ValueError, TypeError):
                percentual_crescimento_atual = 0.0

            try:
                percentual_crescimento_meta = float(percentual_crescimento_meta)
            except (ValueError, TypeError):
                percentual_crescimento_meta = 0.0
                
            fig = go.Figure()

            categorias = ["Cresc. 2025", "Cresc. meta"]
            valores = [percentual_crescimento_atual, percentual_crescimento_meta]
            cores = ["green","aqua"]

            fig.add_trace(go.Bar(
                x=categorias,
                y=valores,
                marker_color=cores,
                text=[f"{v:,.2f} %" for v in valores],
                textposition='outside'
            ))

            fig.update_layout(
                title= f"% Crescimento",
                xaxis_title="",
                yaxis_title="Valor %",
                font=dict(color="white", size=14),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                height=500, 
                width=500
            )
            return fig

        @st.cache_data
        def grafico_linhas_por_filial(mes_referencia, filial_selecionada, ano_selecionado):
            vendas = consultaSQL.obter_vendas_por_mes_e_filial(mes_referencia, filial_selecionada, ano_selecionado)

            if not vendas:
                st.warning("Nenhuma venda encontrada para os filtros selecionados.")
                return None

            valores = [float(v[0]) if isinstance(v[0], Decimal) else v[0] for v in vendas]
            datas = [v[1] for v in vendas]
            meses = [v[2] for v in vendas]
            anos = [v[3] for v in vendas]

            df_vendas = pd.DataFrame({
                "Data": pd.to_datetime(datas),
                "Valor": valores,
                "Mês": [str(m) for m in meses],
                "Ano": [str(a) for a in anos]
            })

            df_vendas["Dia"] = df_vendas["Data"].dt.day 
            df_vendas["Valor_formatado"] = df_vendas["Valor"].apply(lambda x: lc.currency(x, grouping=True))
            df_vendas["MesAno"] = df_vendas["Mês"] + "/" + df_vendas["Ano"]

            fig = go.Figure()

            for mesano in df_vendas["MesAno"].unique():
                df_mesano = df_vendas[df_vendas["MesAno"] == mesano]

                fig.add_trace(go.Scatter(
                    x=df_mesano["Dia"], 
                    y=df_mesano["Valor"],
                    mode='lines+markers',
                    name=mesano,
                    hovertemplate='Dia %{x}<br>Valor: %{customdata}<extra></extra>',
                    customdata=df_mesano["Valor_formatado"]
                ))

            fig.update_layout(
                title=f"📈 Vendas comparadas {mes_referencia[0]} - {filial_selecionada}",
                xaxis_title="Dia do Mês",
                yaxis_title="Vendas (R$)",
                template="plotly_white",
                showlegend=True,
                yaxis=dict(
                    tickprefix="R$ ",
                    separatethousands=True, 
                    tickformat=",."
                )
            )
            return fig

        def grafico_de_evolucao_vendas(vendas_mensais):
            df_vendas = pd.DataFrame(list(vendas_mensais.items()), columns=['Mês', 'Vendas'])
            df_vendas['Mês'] = pd.to_datetime(df_vendas['Mês'], format='%m/%Y')
            df_vendas = df_vendas.sort_values("Mês")

            fig = go.Figure()

            df_vendas["Valor_formatado"] = df_vendas["Vendas"].apply(lambda y: lc.currency(y, grouping=True))

            fig.add_trace(go.Scatter(
                x=df_vendas["Mês"].dt.strftime('%m/%Y'),
                y=df_vendas["Vendas"],
                mode='lines+markers',
                name="Vendas",
                hovertemplate='Mês %{x}<br>Valor: %{customdata}<extra></extra>',
                customdata=df_vendas["Valor_formatado"]
            ))

            fig.update_layout(
                title=f"📊 Vendas nos últimos 12 meses - {filial_selecionada}",
                xaxis_title="Meses",
                yaxis_title="Valor das Vendas (R$)",
                font=dict(color="white", size=14),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                yaxis_tickformat="R$ ,.2f",
                template="plotly_white",
                yaxis=dict(
                    tickprefix="R$ ",
                    separatethousands=True,
                    tickformat=",." 
                )
            )
            return fig

        #Exibição:
        col1, col2, col3 = st.columns(3)

        exibindo_grafico_de_barras = grafico_de_barras_mes_anterior(meta_mes, total_vendas, vendas_mes_atual)
        st.plotly_chart(exibindo_grafico_de_barras, use_container_width=True)

        st.divider()

        exibindo_grafico_de_crescimento = grafico_de_crescimento_mes(percentual_crescimento_atual, percentual_crescimento_meta)
        st.sidebar.plotly_chart(exibindo_grafico_de_crescimento)

        exibindo_grafico_de_linhas_vendas_por_mes = grafico_linhas_por_filial(mes_referencia, filial_selecionada, ano_selecionado)
        if exibindo_grafico_de_linhas_vendas_por_mes is not None:
            st.write(exibindo_grafico_de_linhas_vendas_por_mes)

        exibindo_grafico_acompanhamanto_anual = grafico_de_evolucao_vendas(vendas_mensais)
        st.write(exibindo_grafico_acompanhamanto_anual)



# PÁGINA UNIT

def paginaunit():
    verificar_autenticacao()
    
    # Configuração da página
    st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
    
    # Barra lateral
    if 'user_info' in st.session_state:
        st.sidebar.subheader("Informações do Usuário")
        st.sidebar.write(f"👤 Nome: {st.session_state.user_info['nome']}")
        st.sidebar.write(f"🔑 Permissão: {st.session_state.user_info['permissao']}")
        
        # Adicionar botão Voltar apenas para administradores
        if st.session_state.user_info['permissao'].lower() == 'adm':
            if st.sidebar.button("⬅️ Voltar para Administração"):
                st.session_state.page = 'adm'
                st.rerun()
    
    # Botão sair da conta
    if st.sidebar.button("🚪 Sair"):
        st.session_state.authenticated = False
        st.session_state.page = None
        st.rerun()
    
    # Nome Principal Pagina
    st.title("📊 TESTE")
    
    # Mensagem boas vindas com nome cadastrado na conta
    if 'user_info' in st.session_state:
        st.write(f"Bem-vindo, {st.session_state.user_info['nome']}!")

# PÁGINA RESIDENCIA

def paginaresidencia():
    verificar_autenticacao()
    
    # Configuração da página
    st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
    
    # Barra lateral
    if 'user_info' in st.session_state:
        st.sidebar.subheader("Informações do Usuário")
        st.sidebar.write(f"👤 Nome: {st.session_state.user_info['nome']}")
        st.sidebar.write(f"🔑 Permissão: {st.session_state.user_info['permissao']}")
        
        # Adicionar botão Voltar apenas para administradores
        if st.session_state.user_info['permissao'].lower() == 'adm':
            if st.sidebar.button("⬅️ Voltar para Administração"):
                st.session_state.page = 'adm'
                st.rerun()
    
    # Botão sair da conta
    if st.sidebar.button("🚪 Sair"):
        st.session_state.authenticated = False
        st.session_state.page = None
        st.rerun()
    
    # Nome Principal Pagina
    st.title("📊 Residencia")
    
    # Mensagem boas vindas com nome cadastrado na conta
    if 'user_info' in st.session_state:
        st.write(f"Bem-vindo, {st.session_state.user_info['nome']}!")

# PÁGINA NOVA ADICIONAR....

# SISTEMA DINÂMICO DE ROTEAMENTO

def encontrar_paginas():
    """Lista todas as funções pagina* disponíveis"""
    return [name for name, func in getmembers(sys.modules[__name__]) 
             if name.startswith('pagina') and isfunction(func)]

def main():
    # Pega o nome da página da session_state
    nome_pagina = st.session_state.get('dashboard_page', 'pagina_nao_encontrada')
    
    # Verifica se a função existe
    if nome_pagina in globals() and callable(globals()[nome_pagina]):
        globals()[nome_pagina]()
    else:
        pagina_nao_encontrada()

if __name__ == "__main__":
    main()