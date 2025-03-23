import streamlit as st
import pandas as pd
import requests
import re
import numpy as np

# ================================
# CONFIGURAÇÃO INICIAL
# ================================
st.set_page_config(page_title="Dashboard Previdenciário Profissional", layout="wide")

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
    st.title("📊 Painel Consolidado de DRMs - Dados Públicos 2025")

    df_estrutura = load_csv_sheet()
    st.success("✅ Dados carregados com sucesso!")

    total_drm = df_estrutura[df_estrutura['Nome_Arquivo'].str.contains('DRM', na=False)].shape[0]
    st.markdown(f"🎉 **Total de DRMs encontrados:** {total_drm}")

    st.subheader("📂 DRM 2024 - Estrutura das Pastas e Arquivos - Categorizados por Nome de Arquivo-JM I.A.")

    st.write("🔎 **Filtragem de dados**")
    filtro_nome = st.text_input("🔍 Filtrar por nome do arquivo DRM:", "")

    if filtro_nome:
        df_filtrado = df_estrutura[df_estrutura['Nome_Arquivo'].str.contains(filtro_nome, case=False, na=False)]
    else:
        df_filtrado = df_estrutura.copy()

    st.dataframe(df_filtrado[['Nome_Arquivo', 'Município', 'Mês', 'Ano', 'Estrutura_Nome', 'Link', 'Tipo']])

    st.subheader("📊 Distribuição por Município")
    st.bar_chart(df_filtrado['Município'].value_counts())

    st.subheader("📊 Distribuição por Mês")
    st.bar_chart(df_filtrado['Mês'].value_counts())

    st.subheader("📊 Distribuição por Ano")
    st.bar_chart(df_filtrado['Ano'].value_counts())

    st.subheader("📑 Download dos Dados Filtrados")
    csv_filtered = df_filtrado.to_csv(index=False)
    st.download_button("📥 Baixar CSV Filtrado", csv_filtered, file_name="dados_filtrados_drm.csv")
