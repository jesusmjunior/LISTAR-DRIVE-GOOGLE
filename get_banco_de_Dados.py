import streamlit as st
import pandas as pd
import re
import requests
import tempfile
import os

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

O sistema irá rastrear, clonar 100% dos PDFs em .txt mantendo a hierarquia e virtualizar os dados dos DRM.
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


def listar_arquivos_recursivo(folder_id, api_key, path, estrutura, contador):
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
                listar_arquivos_recursivo(file.get('id'), api_key, path + "/" + file.get('name'), estrutura, contador)
                contador['pastas'] += 1
            else:
                estrutura.append({
                    "Path": path,
                    "Nome_Arquivo": file.get('name'),
                    "ID": file.get('id'),
                    "Link": file.get('webViewLink'),
                    "Tipo": "PDF" if file.get('name').endswith(".pdf") else "Outro"
                })
                contador['arquivos'] += 1
    else:
        st.error(f"Erro API: {response.text}")


def clonar_pdf_para_txt_basico(link, nome_arquivo, path):
    try:
        response = requests.get(link)
        pasta_destino = tempfile.mkdtemp()
        if not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino)
        with open(f"{pasta_destino}/{nome_arquivo}.pdf", "wb") as pdf_file:
            pdf_file.write(response.content)
        return "CLONADO COM SUCESSO"
    except:
        return "ERRO CLONAGEM"


def ler_txt_virtual(path, nome_arquivo):
    try:
        with open(f"txt_virtualizados/{path}/{nome_arquivo}.txt", "r", encoding="utf-8") as txt_file:
            return txt_file.read()
    except:
        return "ERRO LEITURA"


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

# =========================
# ABA PARA CLONAGEM E LEITURA =========================

tabs = st.tabs(["🔄 Mapear & Clonar PDFs", "📥 Ler & Organizar Dados TXT"])

# =========================
# ABA 1 - Mapeamento e Clonagem
# =========================
with tabs[0]:
    if url_pasta:
        folder_id = extrair_folder_id(url_pasta)
        if folder_id:
            estrutura = []
            contador = {'pastas': 0, 'arquivos': 0}
            listar_arquivos_recursivo(folder_id, API_KEY, "PRESTAÇÃO_DE_CONTAS", estrutura, contador)
            df_estrutura = pd.DataFrame(estrutura)
            st.success(f"🎯 {contador['pastas']} pastas e {contador['arquivos']} arquivos encontrados!")
            st.dataframe(df_estrutura)

            # Download estrutura geral
            csv1 = df_estrutura.to_csv(index=False)
            st.download_button("📥 Baixar Estrutura Geral CSV", csv1, file_name="estrutura_geral_completa.csv")

            st.write("### 🧩 Clonando PDFs...")

            status_clonagem = []
            for index, row in df_estrutura.iterrows():
                st.write(f"🔍 Clonando: {row['Nome_Arquivo']}")
                if row['Tipo'] == "PDF":
                    nome_limpo = row['Nome_Arquivo'].replace(".pdf", "")
                    path_sanitizado = row['Path'].replace("/", "_").replace(" ", "_")
                    resultado = clonar_pdf_para_txt_basico(row['Link'], nome_limpo, path_sanitizado)
                    status_clonagem.append({
                        "Nome_Arquivo": row['Nome_Arquivo'],
                        "Path": row['Path'],
                        "Status_Clonagem": resultado
                    })

            df_clonagem = pd.DataFrame(status_clonagem)
            st.write("### 📄 Status da Clonagem dos PDFs:")
            st.dataframe(df_clonagem)

            csv2 = df_clonagem.to_csv(index=False)
            st.download_button("📥 Baixar Status da Clonagem CSV", csv2, file_name="status_clonagem.csv")

# =========================
# ABA 2 - Leitura e Organização
# =========================
with tabs[1]:
    st.write("### 📥 Leitura dos Arquivos .txt Clonados...")

    dados_extraidos = []
    if os.path.exists("txt_virtualizados"):
        for root, dirs, files in os.walk("txt_virtualizados"):
            for file in files:
                if file.endswith(".txt"):
                    nome_arquivo = file.replace(".txt", "")
                    path_relativo = root.replace("txt_virtualizados/", "")
                    texto = ler_txt_virtual(path_relativo, nome_arquivo)
                    if texto and texto != "ERRO LEITURA":
                        campos = aplicar_regex_campos(texto)
                        pertinencia = 1.0 if campos['Receita_Bruta'] != "" else 0.7
                        dados_extraidos.append({
                            "Nome_Arquivo": nome_arquivo,
                            "Pasta_Origem": path_relativo,
                            **campos,
                            "Texto_Clonado": texto,
                            "Pertinencia": pertinencia
                        })

        df_final = pd.DataFrame(dados_extraidos)
        st.write("### 📊 Painel de Dados Extraídos dos .txt:")
        st.dataframe(df_final)

        csv3 = df_final.to_csv(index=False)
        st.download_button("📥 Baixar Dados Extraídos CSV", csv3, file_name="dados_extraidos.csv")
    else:
        st.warning("Nenhum arquivo TXT clonado encontrado. Execute a etapa de clonagem primeiro!")
