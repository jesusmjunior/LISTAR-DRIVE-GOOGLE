import streamlit as st
import pandas as pd
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import tempfile
import openpyxl

# 🟢 CONFIGURAÇÃO STREAMLIT
st.set_page_config(page_title="📂 Google Drive - Lista Arquivos", layout="centered")
st.title("📂 Google Drive - Listar Arquivos")

st.markdown("""
## 👋 Bem-vindo!

1️⃣ Clique abaixo para **Fazer Login com Google**  
2️⃣ Permita o acesso ao seu Google Drive  
3️⃣ Veja sua lista de arquivos!
""")

# 🟢 OAUTH GOOGLE CONFIG
CLIENT_SECRET_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

flow = Flow.from_client_secrets_file(
    CLIENT_SECRET_FILE,
    scopes=SCOPES,
    redirect_uri=st.experimental_get_query_params().get("redirect_uri", ["http://localhost:8501"])[0]
)

auth_url, _ = flow.authorization_url(prompt='consent')
st.write(f"### 🔑 [FAZER LOGIN COM GOOGLE]({auth_url})")

# 🟢 RECEBER CÓDIGO OAUTH
code = st.text_input("👉 Depois de autorizar, copie e cole aqui o código da URL:")

if code:
    try:
        flow.fetch_token(code=code)
        creds = flow.credentials
        service = build('drive', 'v3', credentials=creds)
        arquivos = []
        page_token = None

        st.info("🔄 Buscando arquivos do seu Google Drive...")

        while True:
            response = service.files().list(
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, modifiedTime, webViewLink)",
                pageToken=page_token
            ).execute()
            for arquivo in response.get('files', []):
                arquivos.append({
                    "Nome": arquivo.get('name'),
                    "ID": arquivo.get('id'),
                    "Tipo": arquivo.get('mimeType'),
                    "Última Modificação": arquivo.get('modifiedTime'),
                    "Link": arquivo.get('webViewLink')
                })
            page_token = response.get('nextPageToken', None)
            if not page_token:
                break

        df = pd.DataFrame(arquivos)
        st.success(f"✅ {len(arquivos)} arquivos encontrados!")
        st.dataframe(df)

        # 🟢 EXPORTAÇÃO XLS
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            df.to_excel(tmp.name, index=False)
            st.download_button("📥 Baixar XLS", data=open(tmp.name, 'rb').read(), file_name="meus_arquivos_drive.xlsx")

    except Exception as e:
        st.error(f"Erro: {e}")
