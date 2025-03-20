# Gerando app.py completo com OAuth para qualquer pasta privada do Google Drive

app_py_content = """
import streamlit as st
import pandas as pd
import requests
import re
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# =========================
# CONFIGURAÇÃO DO APP
# =========================
st.set_page_config(page_title="📂 Extrator Google Drive - Adm. Jesus Martins", layout="centered")
st.title("📂 Extrator Google Drive Privado - Adm. Jesus Martins")

st.markdown(\"""
## 🚀 Faça login com sua conta Google e cole o link da pasta do Google Drive!

1️⃣ Faça login com sua conta Google autorizando acesso ao seu Drive.  
2️⃣ Cole abaixo o link da pasta (pode ser privada ou pública).  
3️⃣ Clique em **Extrair Arquivos** para ver todos os arquivos e subpastas!

---  
\""")

# =========================
# OAuth 2.0 CONFIGURAÇÃO
# =========================
CLIENT_ID = "521847155925-b39m4phdl7jisqjjo3t8tnmiintekl7q.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "https://YOUR-STREAMLIT-APP.streamlit.app"  # Substitua pelo seu URL Streamlit Cloud
SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]

# =========================
# AUTENTICAÇÃO OAUTH
# =========================
if 'credentials' not in st.session_state:
    flow = Flow.from_client_config({
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uris": [REDIRECT_URI],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }, scopes=SCOPES, redirect_uri=REDIRECT_URI)

    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true')
    st.markdown(f"[🔑 Clique aqui para login com Google]({auth_url})")
else:
    creds = Credentials(**st.session_state['credentials'])
    service = build('drive', 'v3', credentials=creds)

    # =========================
    # INPUT DO LINK DA PASTA
    # =========================
    url_pasta = st.text_input("🔗 Insira o link da pasta do Google Drive (qualquer pasta privada ou pública):")

    # =========================
    # FUNÇÕES AUXILIARES
    # =========================

    def extrair_folder_id(url):
        match = re.search(r'/folders/([a-zA-Z0-9_-]+)', url)
        if match:
            return match.group(1)
        else:
            return None

    def listar_arquivos(folder_id):
        arquivos = []
        url_base = "https://www.googleapis.com/drive/v3/files"
        params = {
            "q": f"'{folder_id}' in parents",
            "fields": "files(id, name, mimeType, modifiedTime, size, webViewLink)"
        }
        headers = {"Authorization": f"Bearer {creds.token}"}
        response = requests.get(url_base, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            for file in data.get('files', []):
                arquivos.append({
                    "Nome": file.get('name'),
                    "ID": file.get('id'),
                    "Tipo": "Pasta" if file.get('mimeType') == "application/vnd.google-apps.folder" else "Arquivo",
                    "Link": file.get('webViewLink'),
                    "Última Modificação": file.get('modifiedTime', ''),
                    "Tamanho": file.get('size', '—')
                })
            return arquivos
        else:
            st.error(f"Erro ao acessar Google API: {response.text}")
            return []

    # =========================
    # EXECUÇÃO
    # =========================
    if url_pasta:
        folder_id = extrair_folder_id(url_pasta)
        if not folder_id:
            st.error("⚠️ Link inválido! Verifique se é um link válido de pasta do Google Drive.")
        else:
            st.success("✅ Pasta identificada! Clique abaixo para extrair os arquivos:")
            if st.button("📥 Extrair Arquivos"):
                arquivos = listar_arquivos(folder_id)
                if arquivos:
                    df = pd.DataFrame(arquivos)
                    st.success(f"✅ {len(arquivos)} itens encontrados!")
                    st.dataframe(df)

                    # Download CSV
                    csv = df.to_csv(index=False)
                    st.download_button("📄 Baixar lista CSV", csv, file_name="lista_google_drive.csv")
                else:
                    st.warning("Nenhum arquivo encontrado ou erro de permissão.")
"""

# Salvar para entregar
with open("/mnt/data/app_extrator_drive_privado.py", "w", encoding="utf-8") as f:
    f.write(app_py_content)

"/mnt/data/app_extrator_drive_privado.py"
