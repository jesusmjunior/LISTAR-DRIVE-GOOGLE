import streamlit as st
import pandas as pd
import requests

# =========================
# CONFIGURAÇÃO DO DASHBOARD
# =========================
st.set_page_config(page_title="📊 Dashboard DRMs Google Sheets 2025", layout="wide")
st.title("📊 Painel Consolidado de DRMs - Dados Públicos 2025")

# =========================
# GOOGLE SHEETS CONFIGURAÇÃO
# =========================
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSMDcKkFLItxGY0Kb9QBkeQAaYGXYczh0rn7w7bmvQjfSwwCpfo9lNowR4XIPiYNtL4RdGXDUq8NEht/pub?output=csv"
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
# VISUALIZAÇÃO DOS DADOS EM PÁGINAS
# =========================
st.subheader("📋 Dados Consolidados 2025 - Publicação Web")

# Exibindo a tabela completa, mas paginada para 150 linhas por vez
paginas = len(df_estrutura) // 150 + 1
pagina_selecionada = st.slider("Selecione a página:", 1, paginas, 1)

# Exibindo 150 linhas por página
pagina_inicio = (pagina_selecionada - 1) * 150
pagina_fim = pagina_selecionada * 150

st.dataframe(df_estrutura.iloc[pagina_inicio:pagina_fim])

# =========================
# DOWNLOAD CSV DOS DADOS PUBLICADOS
# =========================
csv_download = df_estrutura.to_csv(index=False)
st.download_button("📥 Baixar Dados Publicados em CSV", csv_download, file_name="dados_publicados_2025.csv")
