import streamlit as st
import pandas as pd
import requests
import re

# =========================
# CONFIGURAÇÃO DO DASHBOARD
# =========================
st.set_page_config(page_title="📊 Dashboard DRM Consolidado", layout="wide")
st.title("📊 Painel Consolidado de DRMs - Google Sheets CSV Publicado")

# =========================
# GOOGLE SHEETS CONFIGURAÇÃO
# =========================
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSMDcKkFLItxGY0Kb9QBkeQAaYGXYczh0rn7w7bmvQjfSwwCpfo9lNowR4XIPiYNtL4RdGXDUq8NEht/pub?output=csv"

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
# FUNÇÃO DE SANITIZAÇÃO DE CAMPOS DO DRM
# =========================
def sanitizar_drm_texto(texto):
    dados = {}
    dados['Código Serventia'] = re.search(r'Código da Serventia\s*:?\s*(\d+)', texto)
    dados['Receita Bruta'] = re.search(r'TOTAL DA RECEITA BRUTA\s*R\$\s*([\d\.,]+)', texto)
    dados['Despesa Total'] = re.search(r'TOTAL DESPESAS\s*R\$\s*([\d\.,]+)', texto)
    dados['Saldo a Devolver'] = re.search(r'SALDO A DEVOLVER\s*R\$\s*([\d\.,]+)', texto)
    dados['Teto Constitucional'] = re.search(r'TETO CONSTITUCIONAL\s*R\$\s*([\d\.,]+)', texto)
    dados['Período'] = re.search(r'Per[ií]odo\s*:?\s*(.*?)\s*M[eê]s', texto)
    for key in dados:
        dados[key] = dados[key].group(1).strip() if dados[key] else ''
    return dados

# =========================
# TABELA PRINCIPAL + VISUALIZAR TXT
# =========================
st.subheader("📂 Estrutura das Pastas e Arquivos - Apenas DRMs PDF")

painel_virtual = []

for index, row in df_display.iterrows():
    st.write(f"**📄 {row['Nome_Arquivo']}**")
    st.write(f"📁 Município: {row['Município']} | 🗓️ Mês: {row['Mês']} | Ano: {row['Ano']}")
    st.markdown(row['Link_Clicavel'], unsafe_allow_html=True)
    if st.button(f"📥 Sanitizar e Exibir Dados - {row['Nome_Arquivo']}", key=f"btn_{index}"):
        try:
            response = requests.get(row['Link'])
            texto_extraido = response.content.decode('latin1', errors='ignore')
            dados_sanitizados = sanitizar_drm_texto(texto_extraido)
            st.json(dados_sanitizados)
            painel_virtual.append({
                "Município": row['Município'],
                "Mês": row['Mês'],
                "Ano": row['Ano'],
                "Nome_Arquivo": row['Nome_Arquivo'],
                **dados_sanitizados
            })
        except Exception as e:
            st.error(f"Erro ao sanitizar dados: {e}")

# =========================
# DOWNLOAD CSV CONSOLIDADO + BANCO VIRTUAL TXT
# =========================
if painel_virtual:
    df_virtual = pd.DataFrame(painel_virtual)
    st.subheader("📑 Banco Virtual Sanitizado Consolidado")
    st.dataframe(df_virtual)
    csv_virtual = df_virtual.to_csv(index=False)
    st.download_button("📥 Baixar Banco Virtual Sanitizado CSV", csv_virtual, file_name="banco_virtual_DRM_sanitizado.csv")
