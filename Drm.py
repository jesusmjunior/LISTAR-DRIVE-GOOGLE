import streamlit as st
import pandas as pd
import requests

# =========================
# CONFIGURAÇÃO DO DASHBOARD
# =========================
st.set_page_config(page_title="\ud83d\udcca Dashboard DRMs Google Sheets 2025", layout="wide")
st.title("\ud83d\udcca Painel Consolidado de DRMs - Dados Públicos 2025")

# =========================
# GOOGLE SHEETS CONFIGURAÇÃO
# =========================
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSOJ9l-L3wSq6ZMAAfIkKEIBVVAN5BNRcy3GZGoC0_Reb3dsBmhLFgGJE1hAF5MOnM7iwOTwdl0VkqF/pub?gid=901274610&single=true&output=csv"

# =========================
# LEITURA DIRETA DO CSV PÚBLICO
# =========================
@st.cache_data
def load_csv_sheet():
    df = pd.read_csv(CSV_URL)
    return df

# =========================
# CARREGANDO OS DADOS DO GOOGLE SHEETS
# =========================
df = load_csv_sheet()

st.success("\u2705 Dados carregados com sucesso!")

# =========================
# EXIBIR TOTAL DE DRMs
# =========================
total_drm = df[df['Nome_Arquivo'].str.contains('DRM', na=False)].shape[0]
st.markdown(f"\ud83c\udf89 **Total de DRMs encontrados:** {total_drm}")

# =========================
# EXIBIR TABELA COMPLETA COM OS CAMPOS NOVOS
# =========================
st.subheader("\ud83d\udcc2 Estrutura Completa das Pastas e Arquivos")

# Filtro direto por nome do arquivo (campo livre)
st.write("\ud83d\udd0e **Filtrar por Nome do Arquivo (opcional):**")
filtro_nome = st.text_input("Digite parte do nome do arquivo:", "")

# Aplicar filtro
if filtro_nome:
    df_filtrado = df[df['Nome_Arquivo'].str.contains(filtro_nome, case=False, na=False)]
else:
    df_filtrado = df.copy()

st.dataframe(df_filtrado[['Nome_Arquivo', 'Munic\u00edpio', 'M\u00eas', 'Ano', 'Estrutura_Nome', 'Link', 'Tipo']])

# =========================
# GR\u00c1FICOS DIN\u00c2MICOS
# =========================
st.subheader("\ud83d\udcca Distribui\u00e7\u00e3o por Munic\u00edpio")
st.bar_chart(df_filtrado['Munic\u00edpio'].value_counts())

st.subheader("\ud83d\udcca Distribui\u00e7\u00e3o por M\u00eas")
st.bar_chart(df_filtrado['M\u00eas'].value_counts())

st.subheader("\ud83d\udcca Distribui\u00e7\u00e3o por Ano")
st.bar_chart(df_filtrado['Ano'].value_counts())

# =========================
# DOWNLOAD DOS DADOS FILTRADOS
# =========================
st.subheader("\ud83d\udcc9 Download dos Dados Filtrados")
csv_filtered = df_filtrado.to_csv(index=False)
st.download_button("\ud83d\udcc4 Baixar CSV Filtrado", csv_filtered, file_name="dados_filtrados_drm.csv")
