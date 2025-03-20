import streamlit as st
import requests
import pandas as pd
import re

# =========================
# CONFIGURAÇÃO DO APP
# =========================
st.set_page_config(page_title="📂 Google Drive Público - Leitor de Pastas", layout="centered")
st.title("📂 Leitor de Pasta Google Drive Pública via API")

st.markdown("""
## 🚀 Insira o link público da pasta do Google Drive e extraia todos os arquivos visíveis!

1️⃣ Garanta que a pasta esteja compartilhada como **Qualquer pessoa com o link pode visualizar**.  
2️⃣ Insira abaixo o link.  
3️⃣ Clique em **Extrair Arquivos** para ver todos os arquivos e subpastas!

---  
""")

# =========================
# INPUTS DO USUÁRIO
# =========================
url_pasta = st.text_input("🔗 Insira o link público da pasta:")

api_key = st.text_input("🔑 Insira sua API Key Pública do Google:", type="password")

# =========================
# FUNÇÕES AUXILIARES
# =========================

def extrair_folder_id(url):
    """Extrai o Folder ID da URL fornecida."""
    match = re.search(r'/folders/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    else:
        return None

def listar_arquivos(folder_id, api_key):
    """Consulta a API Google Drive e retorna lista de arquivos/subpastas."""
    arquivos = []
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
            arquivos.append({
                "Nome": file.get('name'),
                "ID": file.get('id'),
                "Tipo": "Pasta" if file.get('mimeType') == "application/vnd.google-apps.folder" else "Arquivo",
                "Link": file.get('webViewLink')
            })
        return arquivos
    else:
        st.error(f"Erro ao acessar Google API: {response.text}")
        return []

# =========================
# EXECUÇÃO
# =========================

if url_pasta and api_key:
    folder_id = extrair_folder_id(url_pasta)
    if not folder_id:
        st.error("⚠️ Link inválido! Verifique se é um link público de pasta do Google Drive.")
    else:
        st.success("✅ Pasta identificada! Clique abaixo para extrair os arquivos:")
        if st.button("📥 Extrair Arquivos"):
            arquivos = listar_arquivos(folder_id, api_key)
            if arquivos:
                df = pd.DataFrame(arquivos)
                st.success(f"✅ {len(arquivos)} itens encontrados!")
                st.dataframe(df)

                # Download CSV
                csv = df.to_csv(index=False)
                st.download_button("📄 Baixar lista CSV", csv, file_name="lista_google_drive.csv")
            else:
                st.warning("Nenhum arquivo encontrado ou erro de permissão.")
