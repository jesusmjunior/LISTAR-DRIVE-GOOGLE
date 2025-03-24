import streamlit as st
import pandas as pd
import numpy as np

# ================================
# CONFIGURAÇÃO INICIAL
# ================================
st.set_page_config(page_title="Dashboard COGEX DRM PRESTAÇÃO DE CONTAS", layout="wide")

# ================================
# LOGIN SIMPLES
# ================================
def login():
    st.title("🔐 Área Protegida - Login Obrigatório")
    user = st.text_input("Usuário (Nome)")
    password = st.text_input("Senha", type="password")

    if (user == "COGEX" and password == "CGX"):
        st.success("Login efetuado com sucesso ✅")
        return True
    else:
        if user and password:
            st.error("Usuário ou senha incorretos ❌")
        return False

# =========================
# GOOGLE SHEETS CONFIGURAÇÃO
# =========================
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSOJ9l-L3wSq6ZMAAfIkKEIBVVAN5BNRcy3GZGoC0_Reb3dsBmhLFgGJE1hAF5MOnM7iwOTwdl0VkqF/pub?gid=901274610&single=true&output=csv"

@st.cache_data
def load_csv_sheet():
    df = pd.read_csv(CSV_URL)
    return df

if login():
    st.title("📊 Painel Consolidado DECLARAÇÃO DE RECEITA MENSAL 2024 COMPLETO TODOS OS .ODS(PLANILHA) E TODOS OS (PDF) ESTÃO SENDO TRATADO E VÃO ALEIMENTAR UMA SO PLANILHA E DASHBOARD (OS DADOS VEM DIRETO DA PASTA DA CAC ")

    df_estrutura = load_csv_sheet()
    st.success("✅ Dados carregados com sucesso!")

    # Criando uma nova coluna para Classificação Semântica
    def classificar_documento(nome):
        nome_upper = nome.upper()
        if 'DRM' in nome_upper:
            return 'DRM'
        elif 'COMPROVANTE' in nome_upper:
            return 'COMPROVANTE'
        elif 'DECLARA' in nome_upper:
            return 'DECLARAÇÃO'
        elif 'DECIS' in nome_upper:
            return 'DECISÃO'
        else:
            return 'OUTROS DOC'

    df_estrutura['Classificação'] = df_estrutura['Nome_Arquivo'].apply(classificar_documento)

    st.subheader("📂 Estrutura das Pastas e Arquivos - Categorizados por Nome de Arquivo")

    # Filtros combinados para cada coluna
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        filtro_class = st.multiselect("Classificação", options=sorted(df_estrutura['Classificação'].unique()))
    with col2:
        filtro_municipio = st.multiselect("Município", options=sorted(df_estrutura['Município'].dropna().unique()))
    with col3:
        filtro_mes = st.multiselect("Mês", options=sorted(df_estrutura['Mês'].dropna().unique()))
    with col4:
        filtro_ano = st.multiselect("Ano", options=sorted(df_estrutura['Ano'].dropna().unique()))
    with col5:
        filtro_tipo = st.multiselect("Tipo", options=sorted(df_estrutura['Tipo'].dropna().unique()))

    df_filtrado = df_estrutura.copy()

    if filtro_class:
        df_filtrado = df_filtrado[df_filtrado['Classificação'].isin(filtro_class)]
    if filtro_municipio:
        df_filtrado = df_filtrado[df_filtrado['Município'].isin(filtro_municipio)]
    if filtro_mes:
        df_filtrado = df_filtrado[df_filtrado['Mês'].isin(filtro_mes)]
    if filtro_ano:
        df_filtrado = df_filtrado[df_filtrado['Ano'].isin(filtro_ano)]
    if filtro_tipo:
        df_filtrado = df_filtrado[df_filtrado['Tipo'].isin(filtro_tipo)]

    # Tornando os links clicáveis
    df_filtrado['Link'] = df_filtrado['Link'].apply(lambda x: f'<a href="{x}" target="_blank">Abrir PDF</a>' if pd.notna(x) else '')

    st.write("\n**Dados Filtrados:**")
    st.write(df_filtrado[['Classificação', 'Nome_Arquivo', 'Município', 'Mês', 'Ano', 'Estrutura_Nome', 'Link', 'Tipo']].to_html(escape=False, index=False), unsafe_allow_html=True)

    st.subheader("📊 Distribuição por Classificação")
    st.bar_chart(df_filtrado['Classificação'].value_counts())

    st.subheader("📊 Distribuição por Município")
    st.bar_chart(df_filtrado['Município'].value_counts())

    st.subheader("📊 Distribuição por Mês")
    st.bar_chart(df_filtrado['Mês'].value_counts())

    st.subheader("📊 Distribuição por Ano")
    st.bar_chart(df_filtrado['Ano'].value_counts())

    st.subheader("📑 Download dos Dados Filtrados")
    csv_filtered = df_filtrado.to_csv(index=False)
    st.download_button("📥 Baixar CSV Filtrado", csv_filtered, file_name="dados_filtrados_drm.csv")
