import numpy as np
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import locale as lc
import consultaSQL
import sys
from inspect import getmembers, isfunction
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta

# Configuração da página DEVE SER A PRIMEIRA COISA
st.set_page_config(page_title="Atos Capital", page_icon="📊", layout="wide")

# Configuração do locale com fallback seguro
try:
    lc.setlocale(lc.LC_ALL, 'pt_BR.UTF-8')
except lc.Error:
    try:
        lc.setlocale(lc.LC_ALL, 'pt_BR')
    except lc.Error:
        lc.setlocale(lc.LC_ALL, 'C')  # Fallback para locale padrão
        st.warning("Locale pt_BR não disponível. Usando configurações padrão.")

# Dicionário de tradução de meses
MESES_TRADUCAO = {
    'January': 'Janeiro',
    'February': 'Fevereiro',
    'March': 'Março',
    'April': 'Abril',
    'May': 'Maio',
    'June': 'Junho',
    'July': 'Julho',
    'August': 'Agosto',
    'September': 'Setembro',
    'October': 'Outubro',
    'November': 'Novembro',
    'December': 'Dezembro'
}

MESES_INGLES = list(MESES_TRADUCAO.keys())
MESES_PORTUGUES = list(MESES_TRADUCAO.values())

def traduzir_mes(mes_ingles):
    """Traduz o nome do mês de inglês para português"""
    return MESES_TRADUCAO.get(mes_ingles, mes_ingles)

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

def format_currency(value):
    try:
        return lc.currency(value, grouping=True, symbol=False)
    except:
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# PÁGINA ATOS
def paginaatos():
    verificar_autenticacao()

    # Barra lateral
    if 'user_info' in st.session_state:
        if st.session_state.user_info['permissao'].lower() == 'adm':
            if st.sidebar.button("⬅️ Voltar para Administração"):
                st.session_state.page = 'adm'
                st.rerun()

    if 'pagina' not in st.session_state:
        st.session_state['pagina'] = 'principal'

    if st.session_state['pagina'] == 'principal':
        def pagina_principal():
            st.markdown(
                """
                <style>
                [data-testid="stSidebar"] {
                    background-color: #800000; 
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            st.sidebar.header("Filtros")
            filiais = consultaSQL.obter_nmfilial()
            filial_selecionada = st.sidebar.selectbox("Selecione a Filial", filiais)

            if st.sidebar.button("Selecionar Meses Anteriores"):
                st.session_state['pagina'] = 'meses_anterior'
                st.rerun()

            mes_referencia = [datetime.now().strftime('%B')]  # Retorna em inglês
            mes_exibicao = traduzir_mes(mes_referencia[0])

            # Cabeçalho
            left_co, cent_co, last_co = st.columns(3)
            with cent_co:
                st.image('logoatos.png', width=500)
            st.write(f"# Relatório de venda da {filial_selecionada} - {mes_exibicao}")

            # Dados
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
                    return float(value) if value is not None else 0.0

                valores = [
                    safe_float(meta_mes),
                    safe_float(previsao),
                    safe_float(acumulo_meta_ano_anterior),
                    safe_float(acumulo_de_vendas)
                ]
                categorias = ["Meta do mês", "Previsão", "Acumulado meta", "Acumulado Vendas"]
                cores = ["darkgray", "darkblue", "darkred", "white"]

                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=categorias,
                    y=valores,
                    marker_color=cores,
                    text=[f"R$ {format_currency(v)}" for v in valores],
                    textposition='outside',
                    hovertext=[f"{cat}<br>R$ {format_currency(v)}" for cat, v in zip(categorias, valores)],
                    hoverinfo='text'
                ))

                fig.update_layout(
                    title=f"📊 Metas e previsões da {filial_selecionada}",
                    xaxis_title="",
                    yaxis_title="Valor (R$)",
                    font=dict(color="white", size=14),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    height=550,
                    yaxis=dict(tickprefix="R$ ", separatethousands=True, tickformat=",.")
                )
                return fig

            @st.cache_data 
            def grafico_de_crescimento(percentual_crescimento_atual, percentual_crescimento_meta):
                valores = [
                    float(percentual_crescimento_atual or 0),
                    float(percentual_crescimento_meta or 0)
                ]
                categorias = ["Cresc. 2025", "Cresc. meta"]
                cores = ["green", "aqua"]

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=categorias,
                    y=valores,
                    marker_color=cores,
                    text=[f"{v:.2f}%" for v in valores],
                    textposition='outside',
                    hovertext=[f"{cat}: {v:.2f}%" for cat, v in zip(categorias, valores)],
                    hoverinfo='text'
                ))

                y_min, y_max = min(valores), max(valores)
                fig.update_layout(
                    title="% Crescimento",
                    xaxis_title="",
                    yaxis_title="Valor %",
                    font=dict(color="white", size=14),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    height=450,
                    margin=dict(t=100, b=50, l=50, r=50),
                    yaxis=dict(range=[y_min - (y_max-y_min)*0.3, y_max + (y_max-y_min)*0.3])
                )
                return fig

            @st.cache_data
            def grafico_linhas_por_filial(mes_referencia, filial_selecionada):
                mes_nome = mes_referencia[0] if isinstance(mes_referencia, list) else mes_referencia
                
                if mes_nome not in MESES_INGLES:
                    st.error(f"Mês inválido: {mes_nome}")
                    return None
                
                vendas = consultaSQL.obter_vendas_por_mes_e_filial(mes_nome, filial_selecionada)
                if not vendas:
                    st.warning("Nenhuma venda encontrada para os filtros selecionados.")
                    return None

                df_vendas = pd.DataFrame({
                    "Data": pd.to_datetime([v[1] for v in vendas]),
                    "Valor": [float(v[0]) if isinstance(v[0], Decimal) else v[0] for v in vendas],
                    "Mês": [str(v[2]) for v in vendas],
                    "Ano": [str(v[3]) for v in vendas]
                })
                df_vendas["Dia"] = df_vendas["Data"].dt.day
                df_vendas["Valor_formatado"] = df_vendas["Valor"].apply(format_currency)
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
                    title=f"📈 Vendas comparadas {traduzir_mes(mes_nome)} - {filial_selecionada}",
                    xaxis_title="Dia do Mês",
                    yaxis_title="Vendas (R$)",
                    template="plotly_white",
                    yaxis=dict(tickprefix="R$ ", separatethousands=True, tickformat=",.")
                )
                return fig

            def grafico_de_evolucao_vendas(vendas_mensais):
                df_vendas = pd.DataFrame(list(vendas_mensais.items()), columns=['Mês', 'Vendas'])
                df_vendas['Mês'] = pd.to_datetime(df_vendas['Mês'], format='%m/%Y')
                df_vendas = df_vendas.sort_values("Mês")
                df_vendas["Valor_formatado"] = df_vendas["Vendas"].apply(format_currency)

                fig = go.Figure()
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
                    template="plotly_white",
                    yaxis=dict(tickprefix="R$ ", separatethousands=True, tickformat=",.")
                )
                return fig

            # Exibição dos gráficos
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"#### Vendas 2024: \nR$ {format_currency(total_vendas)}")
            with col2:
                st.write(f"#### Acumulado 2024: \nR$ {format_currency(acumulo_vendas_ano_anterior)}")
            with col3:
                data_formatada = data_venda_dia.strftime('%d/%m/%Y') if data_venda_dia else 'Sem data'
                st.write(f"#### Vendas do dia: ({data_formatada})\nR$ {format_currency(vendas_dia_anterior)}")

            st.plotly_chart(grafico_de_barras(meta_mes, previsao, acumulo_meta_ano_anterior, acumulo_de_vendas), 
                          use_container_width=True)
            st.divider()

            st.sidebar.plotly_chart(grafico_de_crescimento(percentual_crescimento_atual, percentual_crescimento_meta))
            
            grafico_linhas = grafico_linhas_por_filial(mes_referencia, filial_selecionada)
            if grafico_linhas:
                st.plotly_chart(grafico_linhas, use_container_width=True)

            st.plotly_chart(grafico_de_evolucao_vendas(vendas_mensais), use_container_width=True)

        pagina_principal()
    else:
        def pagina_meses_anterior():
            st.markdown(
                """
                <style>
                [data-testid="stSidebar"] {
                    background-color: #800000; 
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            st.sidebar.header("Filtros")
            filiais = consultaSQL.obter_nmfilial()
            filial_selecionada = st.sidebar.selectbox("Selecione a Filial", filiais)

            hoje = datetime.today()
            anos_disponiveis = consultaSQL.obter_anos_disponiveis()
            ano_selecionado = st.sidebar.selectbox("Selecione o ano de referência", anos_disponiveis, 
                                                 index=len(anos_disponiveis)-1)

            # Determinar meses disponíveis
            if ano_selecionado == hoje.year:
                meses_disponiveis = MESES_INGLES[:hoje.month-1] if hoje.day > 1 else MESES_INGLES[:hoje.month-2]
            else:
                meses_disponiveis = MESES_INGLES

            if not meses_disponiveis:
                st.sidebar.warning("Nenhum mês disponível para seleção")
                mes_referencia = None
            else:
                mes_referencia = st.sidebar.selectbox("Selecione o mês de referência", 
                                                     [traduzir_mes(m) for m in meses_disponiveis])
                mes_referencia = [k for k, v in MESES_TRADUCAO.items() if v == mes_referencia][0]
                # Botão para voltar ao mês atual
                if st.sidebar.button("Voltar para Mês Atual"):
                    st.session_state['pagina'] = 'principal'
                    st.rerun()
            else:
                st.sidebar.warning("Nenhum mês disponível para seleção com base na data atual.")
                mes_referencia = None
                  
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
            # Fim sidebar

            # Início cabeçalho
            left_co, cent_co, last_co = st.columns(3)
            with cent_co:
                st.image('logoatos.png', width=500)
            st.write(f"# Relatório de venda da {filial_selecionada}")
            # Fim cabeçalho

            total_vendas = consultaSQL.obter_vendas_ano_anterior_mes_anterior(filial_selecionada, mes_final, ano_final - 1)
            meta_mes = consultaSQL.obter_meta_mes_anterior(filial_selecionada, mes_final, ano_final)
            vendas_mes_atual = consultaSQL.obter_vendas_mes_anterior(filial_selecionada, mes_final, ano_selecionado)
            percentual_crescimento_meta = consultaSQL.obter_percentual_crescimento_meta_mes_anterior(filial_selecionada)
            vendas_mensais = consultaSQL.obter_vendas_anual_e_filial_mes_anterior(filial_selecionada, mes=mes_final, ano=ano_final)

            def calcular_percentual_crescimento(vendas_mes_atual, total_vendas):
                if total_vendas and total_vendas > 0:
                    percentual = ((vendas_mes_atual / total_vendas) - Decimal("1")) * Decimal("100")
                    return percentual.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                else:
                    return Decimal("0.00")
            percentual_crescimento = calcular_percentual_crescimento(vendas_mes_atual, total_vendas)

            def calcular_percentual_crescimento_meta(vendas_mes_atual, meta_mes):
                if meta_mes and meta_mes > 0:
                    percentual = ((vendas_mes_atual / meta_mes) - Decimal("1")) * Decimal("100")
                    return percentual.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                else:
                    return Decimal("0.00")
            percentual_crescimento_meta = calcular_percentual_crescimento_meta(vendas_mes_atual, meta_mes)

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

                categorias = ["Vendas ano anterior", "Meta do mês", f"Vendas de {mes_selecionado}"]
                valores = [vendas_ano, meta_mes, vendas_mes_atual]
                cores = ["darkgray", "darkblue", "darkred"]
                textos_formatados = [f'R$ {format_currency(v)}' for v in valores]

                fig = go.Figure()

                fig.add_trace(go.Bar(
                    x=categorias,
                    y=valores,
                    marker_color=cores,
                    text=textos_formatados,
                    textposition='outside',
                    hovertemplate=[
                        f'{cat}, {txt}<extra></extra>' for cat, txt in zip(categorias, textos_formatados)
                    ]
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
            def grafico_de_crescimento_mes(vendas_mes_atual, total_vendas, meta_mes):
                try:
                    percentual_crescimento = float(calcular_percentual_crescimento(vendas_mes_atual, total_vendas))
                except (ValueError, TypeError):
                    percentual_crescimento = 0.0

                try:
                    percentual_crescimento_meta = float(calcular_percentual_crescimento_meta(vendas_mes_atual, meta_mes))
                except (ValueError, TypeError):
                    percentual_crescimento_meta = 0.0
                    
                fig = go.Figure()

                categorias = ["Cresc. Mês", "Cresc. meta"]
                valores = [percentual_crescimento, percentual_crescimento_meta]
                cores = ["green", "aqua"]
                
                texto_formatado = [f"{v:.2f}%" for v in valores]
                hover_texto = [f"{cat}: {v:.2f}%" for cat, v in zip(categorias, valores)]

                fig.add_trace(go.Bar(
                    x=categorias,
                    y=valores,
                    marker_color=cores,
                    text=texto_formatado,
                    textposition='outside',
                    hovertext=hover_texto,
                    hoverinfo='text'
                ))
                
                y_min = min(valores)
                y_max = max(valores)
                y_range_margin = (y_max - y_min) * 0.3

                fig.update_layout(
                    title="% Crescimento",
                    xaxis_title="",
                    yaxis_title="Valor %",
                    font=dict(color="white", size=14),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    height=450, 
                    width=450,
                    margin=dict(t=100, b=50, l=50, r=50),
                    yaxis=dict(
                        range=[y_min - y_range_margin, y_max + y_range_margin],
                        zeroline=True,
                        zerolinecolor='gray'
                    )
                )
                return fig

            @st.cache_data
            def grafico_linhas_por_filial(mes_referencia, filial_selecionada, ano_selecionado):
                vendas = consultaSQL.obter_vendas_por_mes_e_filial_mes_anterior(mes_referencia, filial_selecionada, ano_selecionado)

                if not vendas:
                    st.warning("Nenhuma venda encontrada para os filtros selecionados.")
                    return

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
                df_vendas["Valor_formatado"] = df_vendas["Valor"].apply(lambda x: format_currency(x))
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

            def grafico_de_evolucao_vendas_mes_anterior(vendas_mensais, filial, ano):
                df_vendas = pd.DataFrame(list(vendas_mensais.items()), columns=['Mês', 'Vendas'])
                df_vendas['Mês'] = pd.to_datetime(df_vendas['Mês'], format='%m/%Y')
                df_vendas = df_vendas.sort_values("Mês")

                fig = go.Figure()

                df_vendas["Valor_formatado"] = df_vendas["Vendas"].apply(lambda y: format_currency(y))

                fig.add_trace(go.Scatter(
                    x=df_vendas["Mês"].dt.strftime('%m/%Y'),
                    y=df_vendas["Vendas"],
                    mode='lines+markers',
                    name="Vendas",
                    hovertemplate='Mês %{x}<br>Valor: %{customdata}<extra></extra>',
                    customdata=df_vendas["Valor_formatado"]
                ))

                fig.update_layout(
                    title=f"📊 Vendas - Evolução até {mes_final:02d}/{ano} - {filial}",
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

            # Exibição:
            col1, col2, col3 = st.columns(3)

            exibindo_grafico_de_barras = grafico_de_barras_mes_anterior(meta_mes, total_vendas, vendas_mes_atual)
            st.plotly_chart(exibindo_grafico_de_barras, use_container_width=True)

            st.divider()

            exibindo_grafico_de_crescimento = grafico_de_crescimento_mes(vendas_mes_atual, total_vendas, meta_mes)
            st.sidebar.plotly_chart(exibindo_grafico_de_crescimento)

            exibindo_grafico_de_linhas_vendas_por_mes = grafico_linhas_por_filial(mes_referencia, filial_selecionada, ano_selecionado)
            st.write(exibindo_grafico_de_linhas_vendas_por_mes)

            exibindo_grafico_acompanhamanto_mensal = grafico_de_evolucao_vendas_mes_anterior(vendas_mensais, filial_selecionada, ano_selecionado)
            st.write(exibindo_grafico_acompanhamanto_mensal)

        pagina_meses_anterior()

    if st.sidebar.button("🚪 Sair"):
        st.session_state.authenticated = False
        st.session_state.page = None
        st.rerun()

# PÁGINAS UNIT E RESIDENCIA (mantidas como antes)
def paginaunit():
    verificar_autenticacao()
    if 'user_info' in st.session_state:
        st.sidebar.subheader("Informações do Usuário")
        st.sidebar.write(f"👤 Nome: {st.session_state.user_info['nome']}")
        st.sidebar.write(f"🔑 Permissão: {st.session_state.user_info['permissao']}")
        
        if st.session_state.user_info['permissao'].lower() == 'adm':
            if st.sidebar.button("⬅️ Voltar para Administração"):
                st.session_state.page = 'adm'
                st.rerun()
    
    if st.sidebar.button("🚪 Sair"):
        st.session_state.authenticated = False
        st.session_state.page = None
        st.rerun()
    
    st.title("📊 TESTE")
    if 'user_info' in st.session_state:
        st.write(f"Bem-vindo, {st.session_state.user_info['nome']}!")

def paginaresidencia():
    verificar_autenticacao()
    if 'user_info' in st.session_state:
        st.sidebar.subheader("Informações do Usuário")
        st.sidebar.write(f"👤 Nome: {st.session_state.user_info['nome']}")
        st.sidebar.write(f"🔑 Permissão: {st.session_state.user_info['permissao']}")
        
        if st.session_state.user_info['permissao'].lower() == 'adm':
            if st.sidebar.button("⬅️ Voltar para Administração"):
                st.session_state.page = 'adm'
                st.rerun()
    
    if st.sidebar.button("🚪 Sair"):
        st.session_state.authenticated = False
        st.session_state.page = None
        st.rerun()
    
    st.title("📊 Residencia")
    if 'user_info' in st.session_state:
        st.write(f"Bem-vindo, {st.session_state.user_info['nome']}!")

def main():
    nome_pagina = st.session_state.get('dashboard_page', 'pagina_nao_encontrada')
    
    if nome_pagina in globals() and callable(globals()[nome_pagina]):
        globals()[nome_pagina]()
    else:
        pagina_nao_encontrada()

if __name__ == "__main__":
    main()
