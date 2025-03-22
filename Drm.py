import streamlit as st
import pandas as pd
import requests

# =========================
# CONFIGURAÇÃO DO DASHBOARD
# =========================
st.set_page_config(page_title="📊 Dashboard DRM Consolidado", layout="wide")
st.title("📊 Painel Consolidado de DRMs - Google Sheets CSV Publicado")

# =========================
# GOOGLE SHEETS CONFIGURAÇÃO
# =========================
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ9wDOFBPvRLOcGhOUUuX9UKRkned5Fbgg9fzF6LfkiEMpmhovcJkG215YPWmprHnOwgrAA4n-FYD2v/pub?output=csv"

# =========================
# LEITURA DIRETA DO CSV PÚBLICO
# =========================
@st.cache_data
def load_csv_sheet():
    df_estrutura = pd.read_csv(CSV_URL)
    return df_estrutura

st.sidebar.success("✅ Lendo diretamente do CSV Público Consolidado 2025")
df_estrutura = load_csv_sheet()

# =========================
# CONTADORES RESUMIDOS
# =========================
st.subheader("📌 Resumo Geral")
total_pastas = df_estrutura['Path'].nunique()
total_arquivos = len(df_estrutura)
total_drm = df_estrutura[df_estrutura['Tipo'] == 'PDF'].shape[0]

col1, col2, col3 = st.columns(3)
col1.metric("Pastas Únicas", total_pastas)
col2.metric("Total Arquivos", total_arquivos)
col3.metric("Total DRMs", total_drm)

# =========================
# FILTRO POR MUNICÍPIO E MÊS E SOMENTE PDF
# =========================
st.sidebar.subheader("🔎 Filtros")
municipios = df_estrutura['Path'].apply(lambda x: x.split('/')[-1]).unique().tolist()
municipio_selecionado = st.sidebar.selectbox("Selecionar Município", options=["Todos"] + municipios)

meses = df_estrutura['Nome_Arquivo'].apply(lambda x: x.split('-')[1] if '-' in x else '').unique().tolist()
mes_selecionado = st.sidebar.selectbox("Selecionar Mês", options=["Todos"] + meses)

# Filtrando apenas PDF puro DRM
df_drm = df_estrutura[df_estrutura['Tipo'] == 'PDF']
df_display = df_drm.copy()
df_display['Link_Clicavel'] = df_display['Link'].apply(lambda x: f"[Abrir Link]({x})")

# Aplicando filtros
if municipio_selecionado != "Todos":
    df_display = df_display[df_display['Path'].str.contains(municipio_selecionado)]
if mes_selecionado != "Todos":
    df_display = df_display[df_display['Nome_Arquivo'].str.contains(mes_selecionado)]

# Extrair Município, Mês, Ano
df_display['Município'] = df_display['Path'].apply(lambda x: x.split('/')[-1])
df_display['Mês'] = df_display['Nome_Arquivo'].apply(lambda x: x.split('-')[1] if '-' in x else '')
df_display['Ano'] = df_display['Nome_Arquivo'].apply(lambda x: x.split('-')[2] if len(x.split('-')) > 2 else '')

# =========================
# TABELA PRINCIPAL + VISUALIZAR TXT
# =========================
st.subheader("📂 Estrutura das Pastas e Arquivos - Apenas DRMs PDF")

painel_virtual = []

for index, row in df_display.iterrows():
    st.write(f"**📄 {row['Nome_Arquivo']}**")
    st.write(f"📁 Município: {row['Município']} | 🗓️ Mês: {row['Mês']} | Ano: {row['Ano']}")
    st.markdown(row['Link_Clicavel'], unsafe_allow_html=True)
    if st.button(f"📥 Converter e Exibir TXT - {row['Nome_Arquivo']}", key=f"btn_{index}"):
        try:
            response = requests.get(row['Link'])
            texto_extraido = response.content.decode('latin1', errors='ignore')
            st.text_area(f"📄 Conteúdo TXT - {row['Nome_Arquivo']}", value=texto_extraido, height=300)
            painel_virtual.append({
                "Município": row['Município'],
                "Mês": row['Mês'],
                "Ano": row['Ano'],
                "Nome_Arquivo": row['Nome_Arquivo'],
                "Texto": texto_extraido
            })
            st.download_button("📄 Baixar TXT", data=texto_extraido, file_name=f"{row['Nome_Arquivo'].replace('.pdf', '')}.txt")
        except Exception as e:
            st.error(f"Erro ao extrair texto: {e}")

# =========================
# DOWNLOAD CSV CONSOLIDADO + BANCO VIRTUAL TXT
# =========================
csv_download = df_display.to_csv(index=False)
st.download_button("📥 Baixar Estrutura Consolidada CSV", csv_download, file_name="estrutura_consolidada_DRM.csv")

if painel_virtual:
    df_virtual = pd.DataFrame(painel_virtual)
    st.subheader("📑 Banco Virtual Consolidado em TXT")
    st.dataframe(df_virtual)
    csv_virtual = df_virtual.to_csv(index=False)
    st.download_button("📥 Baixar Banco Virtual TXT Consolidado", csv_virtual, file_name="banco_virtual_DRM.csv")
