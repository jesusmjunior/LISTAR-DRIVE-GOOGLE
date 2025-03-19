# Conteúdo do app.py adaptado para uso no Streamlit Cloud usando secrets.toml

app_py_content = """
import streamlit as st
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import pandas as pd
import re
import json

st.set_page_config(page_title="Google Drive Folder File Lister", page_icon="📂")

st.title('📂 Google Drive Folder File Lister')
st.write('Cole abaixo o link da pasta do Google Drive para listar os arquivos (somente arquivos do nível principal).')

# Extrair ID da pasta
def extrair_id_pasta(link):
    match = re.search(r'/folders/([a-zA-Z0-9_-]+)', link)
    if match:
        return match.group(1)
    else:
        return None

# Autenticação via secrets
def google_auth():
    creds_info = {
        "client_id": st.secrets["google_api"]["client_id"],
        "client_secret": st.secrets["google_api"]["client_secret"],
        "refresh_token": st.secrets["google_api"]["refresh_token"],
        "token_uri": "https://oauth2.googleapis.com/token"
    }
    creds = Credentials.from_authorized_user_info(info=creds_info, scopes=["https://www.googleapis.com/auth/drive.metadata.readonly"])
    service = build('drive', 'v3', credentials=creds)
    return service

# Listar arquivos
def listar_arquivos_pasta(service, folder_id):
    query = f"'{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query,
                                   fields="files(id, name, mimeType, modifiedTime, webViewLink)").execute()
    items = results.get('files', [])
    return items

link = st.text_input('Link da Pasta do Google Drive')

if link:
    folder_id = extrair_id_pasta(link)
    if folder_id:
        st.info('🔑 Autenticando com Google...')
        try:
            service = google_auth()
            st.success('✅ Autenticado!')
            
            st.write('🔎 Buscando arquivos...')
            arquivos = listar_arquivos_pasta(service, folder_id)
            
            if arquivos:
                data = []
                for item in arquivos:
                    data.append({
                        'Nome': item['name'],
                        'Tipo (MIME)': item['mimeType'],
                        'Link': item['webViewLink'],
                        'Última Modificação': item['modifiedTime']
                    })
                df = pd.DataFrame(data)
                st.write('### 📋 Arquivos Encontrados:', df)

                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Baixar CSV",
                    data=csv,
                    file_name='lista_arquivos.csv',
                    mime='text/csv',
                )
            else:
                st.warning('Nenhum arquivo encontrado na pasta.')
        except Exception as e:
            st.error(f'Erro: {str(e)}')
    else:
        st.error('❌ Link inválido! Verifique se é um link de pasta válido.')
"""

# Conteúdo do requirements.txt
requirements_content = """
streamlit
google-api-python-client
google-auth
pandas
"""

# Conteúdo do README.md
readme_content = """
# Google Drive Folder File Lister

Este aplicativo permite listar os arquivos de qualquer pasta do Google Drive e gerar um CSV, rodando via Streamlit Cloud.

## Como usar:

1. Clone ou faça fork deste repositório.
2. No Streamlit Cloud, conecte ao repositório.
3. Configure suas credenciais Google Drive em `.streamlit/secrets.toml`.

## Exemplo do arquivo `.streamlit/secrets.toml`:

```toml
[google_api]
client_id = "SEU_CLIENT_ID"
client_secret = "SEU_CLIENT_SECRET"
refresh_token = "SEU_REFRESH_TOKEN"
