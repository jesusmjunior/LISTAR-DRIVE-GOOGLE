import streamlit as st
import pandas as pd
import re
import requests
from io import BytesIO
import os
import PyPDF2

# =========================
# CONFIGURAÇÃO DO APP
# =========================
st.set_page_config(page_title="📂 DRM Extractor - Google Drive", layout="wide")
st.title("📂 DRM Extractor & Virtualization System")

st.markdown("""
### 🚀 Insira o link da pasta Google Drive.
1️⃣ Pasta raiz: **PRESTAÇÃO DE CONTAS**
2️⃣ Subpastas: Nome do Município e mês.
3️⃣ Arquivos: DRM-(MÊS-ANO-SERVENTIA).pdf

O sistema irá rastrear, extrair e virtualizar 100% dos dados dos DRM.
""")

# =========================
# INPUT DO USUÁRIO
# =========================
url_pasta = st.text_input("🔗 Insira o link público da pasta:")

# =========================
# SUA API KEY CONFIGURADA
# =========================
API_KEY = "AIzaSyAKibc0A3TerDdfQeZBLePxU01PbK_53Lw"

# =========================
# FUNÇÕES AUXILIARES
# =========================

def extrair_folder_id(url):
    match = re.search(r'/folders/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    return None


def listar_arquivos_recursivo(folder_id, api_key, path, estrutura):
    url_base = "https://www.googleapis.com/drive/v3/files"
    params = {
        "q": f"'{folder_id}' in parents",
        "fields": "files(id, name, mimeType, webViewLink)",
        "key": api_key
    }
    response = requests.get(url_base, params=params)
    if response.status_code == 200:
        data = response.json()
        for file in data.get('files', []):
            if file.get('mimeType') == "application/vnd.google-apps.folder":
                listar_arquivos_recursivo(file.get('id'), api_key, path + "/" + file.get('name'), estrutura)
            else:
                estrutura.append({
                    "Path": path,
                    "Nome_Arquivo": file.get('name'),
                    "ID": file.get('id'),
                    "Link": file.get('webViewLink'),
                    "Tipo": "PDF" if file.get('name').endswith(".pdf") else "Outro"
                })
    else:
        st.error(f"Erro API: {response.text}")


def extrair_texto_pdf(link):
    try:
        response = requests.get(link)
        with BytesIO(response.content) as f:
            reader = PyPDF2.PdfReader(f)
            texto = ""
            for page in reader.pages:
                texto += page.extract_text() or ""
        return texto
    except:
        return "ERRO EXTRAÇÃO"


def aplicar_regex_campos(texto):
    campos = {}
    campos['Receita_Bruta'] = re.search(r'TOTAL DA RECEITA BRUTA R\$(.*?)\n', texto)
    campos['Despesa_Total'] = re.search(r'TOTAL DESPESAS R\$ (.*?)\n', texto)
    campos['Receita_Liquida'] = re.search(r'RECEITA L[IÍ]QUIDA R\$ (.*?)\n', texto)
    campos['Saldo_Dev'] = re.search(r'SALDO A DEVOLVER R\$ (.*?)\n', texto)
    campos['Teto_Constitucional'] = re.search(r'TETO CONSTITUCIONAL R\$ (.*?)\n', texto)
    campos['Data_Periodo'] = re.search(r'Per[ií]odo (.*?) M[eê]s:', texto)
    campos['Codigo_Serventia'] = re.search(r'Código da Serventia: (\d+)', texto)
    for key in campos:
        campos[key] = campos[key].group(1).strip() if campos[key] else ""
    return campos


def salvar_txt_virtual(link, nome_arquivo):
    try:
        response = requests.get(link)
        with BytesIO(response.content) as f:
            reader = PyPDF2.PdfReader(f)
            texto = ""
            for page in reader.pages:
                texto += page.extract_text() or ""
        if not os.path.exists("txt_virtualizados"):
            os.makedirs("txt_virtualizados")
        with open(f"txt_virtualizados/{nome_arquivo}.txt", "w", encoding="utf-8") as txt_file:
            txt_file.write(texto)
        return texto
    except:
        return "ERRO EXTRAÇÃO"


def ler_txt_virtual(nome_arquivo):
    try:
        with open(f"txt_virtualizados/{nome_arquivo}.txt", "r", encoding="utf-8") as txt_file:
            return txt_file.read()
    except:
        return "ERRO LEITURA"

# =========================
# PROCESSAMENTO PRINCIPAL
# =========================

if url_pasta:
    folder_id = extrair_folder_id(url_pasta)
    if folder_id:
        estrutura = []
        listar_arquivos_recursivo(folder_id, API_KEY, "PRESTAÇÃO DE CONTAS", estrutura)
        df_estrutura = pd.DataFrame(estrutura)
        st.success(f"🎯 {len(df_estrutura)} arquivos encontrados e organizados!")
        st.dataframe(df_estrutura)

        st.write("### 🧩 Iniciando Extração e Virtualização em .txt...")

        dados_extraidos = []
        painel_dados = []
        for index, row in df_estrutura.iterrows():
            st.write(f"🔍 Processando: {row['Nome_Arquivo']}")
            if row['Tipo'] == "PDF":
                nome_limpo = row['Nome_Arquivo'].replace(".pdf", "")
                texto = salvar_txt_virtual(row['Link'], nome_limpo)
                campos = aplicar_regex_campos(texto)
                pertinencia = 1.0 if campos['Receita_Bruta'] != "" else 0.7
                dados_extraidos.append({
                    "Path": row['Path'],
                    "Nome_Arquivo": row['Nome_Arquivo'],
                    "Link": row['Link'],
                    **campos,
                    "Texto_Completo": texto,
                    "Pertinencia": pertinencia
                })
                painel_dados.append({
                    "Municipio": row['Path'].split("/")[-1],
                    "Mes_Ano": row['Path'].split("/")[-2] if len(row['Path'].split("/")) > 2 else "",
                    "Nome_Arquivo": row['Nome_Arquivo'],
                    "Texto_Clonado": texto
                })

        df_final = pd.DataFrame(dados_extraidos)
        df_painel = pd.DataFrame(painel_dados)
        st.write("### 📄 Banco Virtual de Dados Completos:")
        st.dataframe(df_final)

        st.write("### 📊 Painel Informacional Consolidado:")
        st.dataframe(df_painel)

        csv1 = df_estrutura.to_csv(index=False)
        csv2 = df_final.to_csv(index=False)
        csv3 = df_painel.to_csv(index=False)
        st.download_button("📥 Baixar Estrutura Geral CSV", csv1, file_name="estrutura_geral.csv")
        st.download_button("📥 Baixar Dados Extraídos CSV", csv2, file_name="dados_extraidos.csv")
        st.download_button("📥 Baixar Painel Consolidado CSV", csv3, file_name="painel_consolidado.csv")
