# Preparando estrutura completa do projeto para Streamlit Cloud e GitHub (100% online)

# Conteúdo do app.py adaptado para 100% online (Streamlit Cloud)
app_py_content = """
import streamlit as st
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import pandas as pd
import re

st.set_page_config(page_title="Google Drive Folder Lister", page_icon="📂")

st.title('📂 Google Drive Folder File Lister')
st.write('Cole abaixo o link da pasta do Google Drive para listar os arquivos (nível principal).')

# Função para extrair ID da pasta
def extrair_id_pasta(link):
    match = re.search(r'/folders/([a-zA-Z0-9_-]+)', link)
    if match:
        return match.group(1)
    else:
        return None

# Autenticação usando secrets do Streamlit Cloud
def google_auth():
    creds_info = {
        "token": st.secrets["google_api"]["token"],
        "refresh_token": st.secrets["google_api"]["refresh_token"],
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": st.secrets["google_api"]["client_id"],
        "client_secret": st.secrets["google_api"]["client_secret"],
        "scopes": ["https://www.googleapis.com/auth/drive.metadata.readonly"]
    }
    creds = Credentials.from_authorized_user_info(info=creds_info)
    service = build('drive', 'v3', credentials=creds)
    return service

# Função para listar arquivos da pasta
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

# requirements.txt para rodar no Streamlit Cloud
requirements_content = """
streamlit
google-api-python-client
google-auth
pandas
"""

# README explicando tudo para GitHub + Streamlit Cloud
readme_content = """
# Google Drive Folder File Lister (100% Online)

Este aplicativo lista os arquivos de qualquer pasta do Google Drive e gera um CSV. Roda totalmente no **Streamlit Cloud**, conectado ao seu repositório no **GitHub**.

## Como Usar:

1. Suba este repositório para seu GitHub.
2. No [Streamlit Cloud](https://streamlit.io/cloud), conecte ao repositório.
3. Em **Settings → Secrets**, configure suas credenciais Google:

