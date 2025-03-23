import streamlit as st
import pandas as pd
import numpy as np
from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from odf.text import P
import requests
from io import BytesIO

# ================================
# CONFIGURAÇÃO INICIAL
# ================================
st.set_page_config(page_title="GET.SCRAPING - Coleta de Dados ODS", layout="wide")
st.title("📥 GET.SCRAPING - Coletor Modular de Dados dos DRMs (.ods)")

# ================================
# API GOOGLE DRIVE (Caso necessário)
# ================================
API_KEY = "AIzaSyAKibc0A3TerDdfQeZBLePxU01PbK_53Lw"

# ================================
# URL DO CSV PÚBLICO
# ================================
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSOJ9l-L3wSq6ZMAAfIkKEIBVVAN5BNRcy3GZGoC0_Reb3dsBmhLFgGJE1hAF5MOnM7iwOTwdl0VkqF/pub?gid=901274610&single=true&output=csv"

@st.cache_data
def load_csv_sheet():
    df = pd.read_csv(CSV_URL)
    return df

# ================================
# FUNÇÃO PARA EXTRAIR TEXTO DE .ODS
# ================================
def extrair_dados_ods(file_content):
    try:
        doc = load(file_content)
        texto = []
        for table in doc.spreadsheet.getElementsByType(Table):
            for row in table.getElementsByType(TableRow):
                linha = []
                for cell in row.getElementsByType(TableCell):
                    ps = cell.getElementsByType(P)
                    cell_text = " ".join([str(p) for p in ps])
                    linha.append(cell_text)
                if any(linha):
                    texto.append(linha)
        return texto
    except Exception as e:
        return [[f"Erro ao processar: {e}"]]

# ================================
# CARREGANDO OS DADOS DO GOOGLE SHEETS
# ================================
df_estrutura = load_csv_sheet()

st.success("✅ Dados carregados com sucesso!")

# Filtrar arquivos .ods
st.subheader("🔎 Filtrar Arquivos ODS")
df_ods = df_estrutura[df_estrutura['Nome_Arquivo'].str.lower().str.endswith('.ods')].reset_index(drop=True)
st.write(f"Total de arquivos .ods encontrados: {df_ods.shape[0]}")

# ================================
# DOWNLOAD E PROCESSAMENTO EM LOTE
# ================================
lote_tamanho = st.slider("Selecione o tamanho do lote para baixar e processar:", 5, 50, 10)
processar = st.button("🚀 Iniciar Coleta e Processamento")

if processar:
    resultados = []

    progress_bar = st.progress(0)
    total = df_ods.shape[0]

    for idx, row in df_ods.iterrows():
        try:
            link = row['Link']
            response = requests.get(link)
            if response.status_code == 200:
                conteudo_arquivo = BytesIO(response.content)
                texto_extraido = extrair_dados_ods(conteudo_arquivo)
                resultados.append({
                    "Nome_Arquivo": row['Nome_Arquivo'],
                    "Município": row['Município'],
                    "Mês": row['Mês'],
                    "Ano": row['Ano'],
                    "Conteudo Extraido": texto_extraido[:5]  # Exibir só prévia
                })
        except Exception as e:
            resultados.append({
                "Nome_Arquivo": row['Nome_Arquivo'],
                "Município": row['Município'],
                "Mês": row['Mês'],
                "Ano": row['Ano'],
                "Erro": str(e)
            })
        if (idx+1) % lote_tamanho == 0 or idx == total-1:
            progress_bar.progress((idx+1)/total)

    st.success("✅ Coleta concluída!")

    df_resultado = pd.DataFrame(resultados)
    st.dataframe(df_resultado)

    csv_export = df_resultado.to_csv(index=False)
    st.download_button("📥 Baixar Dados Extraídos", csv_export, file_name="dados_ods_extraidos.csv")
