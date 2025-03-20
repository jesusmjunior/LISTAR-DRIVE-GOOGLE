import streamlit as st
import pandas as pd
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import tempfile
import openpyxl
import pdfplumber  # Agora corrigido e funcionando

st.set_page_config(page_title="Listar Arquivos Google Drive", layout="centered")

st.title("📂 Google Drive - Listar Arquivos")
st.markdown("""
## 👋 Bem-vindo!

Para listar os arquivos do seu Google Drive, siga os passos:

1️⃣ Clique no botão abaixo para **Fazer Login com sua Conta Google**.  
2️⃣ **Permita o acesso ao seu Google Drive**.  
3️⃣ Seus arquivos serão listados abaixo!  
""")

# Configuração OAuth
CLIENT_SECRET_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

flow = Flow.from_client_secrets_file(
    CLIENT_SECRET_FILE,
    scopes=SCOPES,
    redirect_uri=st.experimental_get_query_params().get("redirect_uri", ["http://localhost:8501"])[0]
)

auth_url, _ = flow.authorization_url(prompt='consent')

st.write(f"### 🔑 [FAZER LOGIN COM GOOGLE]({auth_url})")

code = st.text_input("👉 Depois de autorizar, copie e cole o código da URL aqui:")

if code:
    flow.fetch_token(code=code)
    creds = flow.credentials
    try:
        service = build('drive', 'v3', credentials=creds)
        arquivos = []
        page_token = None

        st.info("🔄 Buscando arquivos do seu Drive...")

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
        st.success(f"✅ {len(arquivos)} arquivos encontrados no seu Google Drive!")
        st.dataframe(df)

        # Exportação XLS
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            df.to_excel(tmp.name, index=False)
            st.download_button("📥 Baixar Lista XLS", data=open(tmp.name, 'rb').read(), file_name="meus_arquivos_drive.xlsx")

        # NOVO BLOCO: Upload e extração de PDF
        st.markdown("## 📄 Upload e Extração de Dados de PDF")
        uploaded_pdf = st.file_uploader("Faça upload de um arquivo PDF para extrair texto", type=["pdf"])
        if uploaded_pdf is not None:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_pdf:
                tmp_pdf.write(uploaded_pdf.read())
                extracted_data = []
                with pdfplumber.open(tmp_pdf.name) as pdf:
                    for page in pdf.pages:
                        extracted_data.append(page.extract_text())
                st.success("✅ Texto extraído do PDF:")
                st.text('\n\n'.join(extracted_data))

    except Exception as e:
        st.error(f"Erro ao acessar o Drive: {e}")
