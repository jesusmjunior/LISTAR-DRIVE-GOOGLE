import streamlit as st
import pandas as pd
import re
import requests
import fitz  # PyMuPDF
from sympy import symbols, Piecewise

# =====================
# CONFIGURAÇÃO INICIAL
# =====================
st.set_page_config(page_title="📂 DRM Extractor - Google Drive", layout="wide")
st.title("📂 DRM Extractor & Virtualization System")

st.markdown("""
### 🚀 Insira o link da pasta Google Drive ou carregue CSV com múltiplos links.
1️⃣ Pasta raiz: **PRESTAÇÃO DE CONTAS**
2️⃣ Subpastas: Nome do Município e mês.
3️⃣ Arquivos: DRM-(MÊS-ANO-SERVENTIA).pdf

O sistema irá rastrear, extrair e virtualizar 100% dos dados dos DRM.
""")

# =====================
# INPUT DO USUÁRIO
# =====================
input_type = st.radio("Selecione o tipo de entrada:", ("Link Único", "CSV com múltiplos links"))

link_list = []
if input_type == "Link Único":
    url_pasta = st.text_input("🔗 Insira o link público da pasta:")
    if url_pasta:
        link_list.append(url_pasta)
else:
    uploaded_csv = st.file_uploader("📄 Carregue o arquivo CSV:", type=["csv"])
    if uploaded_csv:
        df_links = pd.read_csv(uploaded_csv)
        link_list.extend(df_links.iloc[:, 0].tolist())

API_KEY = "AIzaSyAKibc0A3TerDdfQeZBLePxU01PbK_53Lw"

# =====================
# FUNÇÕES AUXILIARES
# =====================

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
        with open("temp.pdf", "wb") as f:
            f.write(response.content)
        doc = fitz.open("temp.pdf")
        texto = "\n".join([page.get_text() for page in doc])
        doc.close()
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

# =====================
# MODELO FUZZY (PERTINÊNCIA)
# =====================

x = symbols('x')
pertinencia_formula = Piecewise((1.0, x >= 0.9), (0.7, (x < 0.9) & (x >= 0.6)), (0.0, x < 0.6))
st.latex(r"\mu_{DRM}(x) = \begin{cases} 1.0 & \text{se } x \geq 0.9 \\ 0.7 & \text{se } 0.6 \leq x < 0.9 \\ 0.0 & \text{se } x < 0.6 \end{cases}")

# =====================
# PROCESSAMENTO PRINCIPAL
# =====================

if link_list:
    estrutura = []
    dados_extraidos = []
    for link in link_list:
        folder_id = extrair_folder_id(link)
        if folder_id:
            listar_arquivos_recursivo(folder_id, API_KEY, "PRESTAÇÃO DE CONTAS", estrutura)

    df_estrutura = pd.DataFrame(estrutura)
    st.success(f"🎯 {len(df_estrutura)} arquivos encontrados e organizados!")
    st.dataframe(df_estrutura)

    st.write("### 🧩 Iniciando Extração de Dados...")

    for index, row in df_estrutura.iterrows():
        st.write(f"🔍 Processando: {row['Nome_Arquivo']}")
        if row['Tipo'] == "PDF":
            texto = extrair_texto_pdf(row['Link'])
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

    df_final = pd.DataFrame(dados_extraidos)
    st.write("### 📄 Banco Virtual de Dados Completos:")
    st.dataframe(df_final)

    csv1 = df_estrutura.to_csv(index=False)
    csv2 = df_final.to_csv(index=False)
    st.download_button("📥 Baixar Estrutura Geral CSV", csv1, file_name="estrutura_geral.csv")
    st.download_button("📥 Baixar Dados Extraídos CSV", csv2, file_name="dados_extraidos.csv")
