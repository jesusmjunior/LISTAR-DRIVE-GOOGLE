import streamlit as st
import pandas as pd

# =========================
# CONFIGURAÇÃO DO DASHBOARD
# =========================
st.set_page_config(page_title="📊 Dashboard DRM Consolidado", layout="wide")
st.title("📊 Painel Consolidado de DRMs")

# =========================
# UPLOAD DOS ARQUIVOS CSV
# =========================

st.sidebar.header("📂 Upload dos Arquivos")
estrutura_csv = st.sidebar.file_uploader("🔽 Upload Estrutura Geral CSV", type=["csv"])
clonagem_csv = st.sidebar.file_uploader("🔽 Upload Status Clonagem CSV", type=["csv"])

if estrutura_csv and clonagem_csv:
    df_estrutura = pd.read_csv(estrutura_csv)
    df_clonagem = pd.read_csv(clonagem_csv)

    st.success("✅ Arquivos carregados com sucesso!")

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
    # FILTRO POR MUNICÍPIO E MÊS
    # =========================
    st.sidebar.subheader("🔎 Filtros")
    municipios = df_estrutura['Path'].apply(lambda x: x.split('/')[-1]).unique().tolist()
    municipio_selecionado = st.sidebar.selectbox("Selecionar Município", options=["Todos"] + municipios)

    meses = df_estrutura['Nome_Arquivo'].apply(lambda x: x.split('-')[1] if '-' in x else '').unique().tolist()
    mes_selecionado = st.sidebar.selectbox("Selecionar Mês", options=["Todos"] + meses)

    df_display = df_estrutura.merge(df_clonagem[['Nome_Arquivo', 'Status_Clonagem']], on='Nome_Arquivo', how='left')
    df_display['Link_Clicavel'] = df_display['Link'].apply(lambda x: f"[Abrir Link]({x})")
    df_display['Status_Icone'] = df_display['Status_Clonagem'].apply(lambda x: '🟢 Sucesso' if x=="CLONADO COM SUCESSO" else '🔴 Falha')

    # Aplicando filtros
    if municipio_selecionado != "Todos":
        df_display = df_display[df_display['Path'].str.contains(municipio_selecionado)]
    if mes_selecionado != "Todos":
        df_display = df_display[df_display['Nome_Arquivo'].str.contains(mes_selecionado)]

    # =========================
    # TABELA PRINCIPAL
    # =========================
    st.subheader("📂 Estrutura das Pastas e Arquivos")
    st.dataframe(df_display[['Path', 'Nome_Arquivo', 'Tipo', 'Link_Clicavel', 'Status_Icone']])

    # =========================
    # DOWNLOAD CSV CONSOLIDADO
    # =========================
    csv_download = df_display.to_csv(index=False)
    st.download_button("📥 Baixar Estrutura Consolidada CSV", csv_download, file_name="estrutura_consolidada.csv")

else:
    st.info("⏳ Aguarde... Faça upload dos arquivos CSV na barra lateral para iniciar o painel.")
