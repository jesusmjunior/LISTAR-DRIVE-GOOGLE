# Criando o arquivo app.py para o projeto Streamlit

app_py_content = """
import streamlit as st
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import pandas as pd
import os
import re

# Google API escopo
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

# Autenticação Google
def google_auth():
    creds = None
    if os.path.exists('token.pkl'):
        with open('token.pkl', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pkl', 'wb') as token:
            pickle.dump(creds, token)
    service = build('drive', 'v3', credentials=creds)
    return service

# Extrair ID da pasta a partir do link
def extrair_id_pasta(link):
    match = re.search(r'/folders/([a-zA-Z0-9_-]+)', link)
    if match:
        return match.group(1)
    else:
        return None

# Listar arquivos no nível principal da pasta
def listar_arquivos_pasta(service, folder_id):
    query = f"'{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query,
                                   fields="files(id, name, mimeType, modifiedTime, webViewLink)").execute()
    items = results.get('files', [])
    return items

# Streamlit App
st.title('📂 Google Drive Folder File Lister')
st.write('Cole abaixo o link da pasta do Google Drive para listar os arquivos.')

link = st.text_input('Link da Pasta do Google Drive')

if link:
    folder_id = extrair_id_pasta(link)
    if folder_id:
        st.info('🔑 Autenticando com Google...')
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

            # Download CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar CSV",
                data=csv,
                file_name='lista_arquivos.csv',
                mime='text/csv',
            )
        else:
            st.warning('Nenhum arquivo encontrado na pasta.')
    else:
        st.error('❌ Link inválido! Verifique se é um link de pasta válido.')
"""

# Salvar o app.py
    f.write(app_py_content)

"/mnt/data/app.py"
