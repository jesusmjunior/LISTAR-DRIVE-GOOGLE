import streamlit as st
import pandas as pd
import requests
import re

# =========================
# CONFIGURAÇÃO DO DASHBOARD
# =========================
st.set_page_config(page_title="📊 Dashboard DRMs Google Sheets 2025", layout="wide")
st.title("📊 Painel Consolidado de DRMs - Dados Públicos 2025")

# =========================
# GOOGLE SHEETS CONFIGURAÇÃO
# =========================
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSMDcKkFLItxGY0Kb9QBkeQAaYGXYczh0rn7w7bmvQjfSwwCpfo9lNowR4XIPiYNtL4RdGXDUq8NEht/pub?gid=1916790160&single=true&output=csv"
API_KEY = "AIzaSyAKibc0A3TerDdfQeZBLePxU01PbK_53Lw"

# =========================
# LEITURA DIRETA DO CSV PÚBLICO
# =========================
@st.cache_data
def load_csv_sheet():
    df_estrutura = pd.read_csv(CSV_URL)
    return df_estrutura

# =========================
# CARREGANDO OS DADOS DO GOOGLE SHEETS
# =========================
df_estrutura = load_csv_sheet()

st.success("✅ Dados carregados com sucesso!")

# =========================
# FILTROS POR MUNICÍPIO E MÊS
# =========================
st.sidebar.subheader("🔎 Filtros")
municipios = df_estrutura['Path'].apply(lambda x: x.split('/')[-1]).unique().tolist()
municipio_selecionado = st.sidebar.selectbox("Selecionar Município", options=["Todos"] + municipios)

meses = df_estrutura['Nome_Arquivo'].apply(lambda x: x.split('-')[1] if '-' in x else '').unique().tolist()
mes_selecionado = st.sidebar.selectbox("Selecionar Mês", options=["Todos"] + meses)

# =========================
# EXIBIR TABELA FILTRADA COM DECOMPOSIÇÃO DO NOME DO ARQUIVO
# =========================
df_estrutura['Categoria'] = df_estrutura['Nome_Arquivo'].apply(lambda x: 'DRM' if 'DRM' in x else ('DECISÃO' if 'DECISÃO' in x else ('DECLARAÇÃO' if 'DECLARAÇÃO' in x else ('MINUTA' if 'MINUTA' in x else 'OUTRO'))))

# Aplicando filtros
if municipio_selecionado != "Todos":
    df_estrutura = df_estrutura[df_estrutura['Path'].str.contains(municipio_selecionado)]
if mes_selecionado != "Todos":
    df_estrutura = df_estrutura[df_estrutura['Nome_Arquivo'].str.contains(mes_selecionado)]

# =========================
# EXIBIR TABELA COM CATEGORIAS E DADOS
# =========================
st.subheader("📂 Estrutura das Pastas e Arquivos - Categorizados por Nome de Arquivo")
st.dataframe(df_estrutura[['Nome_Arquivo', 'Categoria', 'Link']])

# =========================
# GRÁFICOS: CATEGORIAS E NÚMEROS
# =========================
st.subheader("📊 Gráfico: Distribuição por Categoria")

# Contagem por categoria
categoria_count = df_estrutura['Categoria'].value_counts()

# Gerar gráfico de barras usando gráfico nativo do Streamlit
st.bar_chart(categoria_count)

# =========================
# FUNÇÃO DE SANITIZAÇÃO DOS DADOS DO PDF
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
# TABELA DE SANITIZAÇÃO COM DADOS DO PDF
# =========================
# Exibindo a categoria 'DRM' com sanitização
painel_virtual = []

for index, row in df_estrutura[df_estrutura['Categoria'] == 'DRM'].iterrows():
    st.write(f"**📄 {row['Nome_Arquivo']}**")
    st.write(f"📁 Path: {row['Path']} | 🗓️ Tipo: {row['Categoria']}")
    st.markdown(f"[Abrir Link]({row['Link']})", unsafe_allow_html=True)
    try:
        response = requests.get(row['Link'])
        texto_extraido = response.content.decode('latin1', errors='ignore')
        dados_sanitizados = sanitizar_drm_texto(texto_extraido)
        st.json(dados_sanitizados)
        painel_virtual.append({
            "Nome_Arquivo": row['Nome_Arquivo'],
            "Path": row['Path'],
            "Categoria": row['Categoria'],
            **dados_sanitizados
        })
    except Exception as e:
        st.error(f"Erro ao sanitizar dados: {e}")

# =========================
# DOWNLOAD DOS DADOS SANITIZADOS
# =========================
if painel_virtual:
    df_virtual = pd.DataFrame(painel_virtual)
    st.subheader("📑 Banco Virtual Sanitizado Consolidado")
    st.dataframe(df_virtual)
    csv_virtual = df_virtual.to_csv(index=False)
    st.download_button("📥 Baixar Banco Virtual Sanitizado CSV", csv_virtual, file_name="banco_virtual_DRM_sanitizado.csv")

# =========================
# ABA ADICIONAL - FILTRO DE DRMS DO GOOGLE SHEET
# =========================
tabs = st.tabs(["📊 Painel Consolidado", "🔍 Filtro de DRMs do Google Sheets"])

with tabs[1]:
    st.subheader("🔎 Filtragem de Dados DRM")
    st.write("Com base no nome do arquivo e na estrutura de dados dos DRMs.")

    filtro_nome = st.text_input("🔍 Filtrar por nome do arquivo DRM:", "")

    # Leitura do Google Sheets
    df_sheets = pd.read_csv(CSV_URL)

    # Filtragem
    df_sheets_filtered = df_sheets[df_sheets['Nome_Arquivo'].str.contains(filtro_nome, case=False)]

    # Exibir dados filtrados
    st.dataframe(df_sheets_filtered)

    # DOWNLOAD CSV FILTRADO
    csv_filtered = df_sheets_filtered.to_csv(index=False)
    st.download_button("📥 Baixar Dados Filtrados CSV", csv_filtered, file_name="dados_filtrados_drm.csv")
