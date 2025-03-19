import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import pandas as pd
import re

# Configuração da página
st.set_page_config(
    page_title="Adm. Jesus Martins - Extratador de dados do Google Drive",
    page_icon="📂"
)

st.title('📂 Adm. Jesus Martins - Extratador de dados do Google Drive')
st.write('Faça login com seu Google para listar seus arquivos e gerar relatório.')

# CONFIGURAÇÃO OAuth 2.0 (SUBSTITUA PELO SEU CLIENT ID PÚBLICO!)
client_config = {
  "web": {
    "client_id": "YOUR_PUBLIC_CLIENT_ID.apps.googleusercontent.com",  # <<<<< Coloque aqui seu client_id do Google
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "redirect_uris": ["https://YOUR-STREAMLIT-APP.streamlit.app"],  # <<<<< Coloque o URL do seu Streamlit Cloud
    "project_id": "streamlit-drive-extractor"
  }
}

scopes = ["https://www.googleapis.com/auth/drive.metadata.readonly"]

# Verifica se já está autenticado
if 'credentials' not in st.session_state:
    flow = Flow.from_client_config(client_config, scopes=scopes, redirect_uri=client_config['web']['redirect_uris'][0])
    auth_url, _ = flow.authorization_url(prompt='consent')
    st.markdown(f"[🔑 Clique aqui para login com Google]({auth_url})")
else:
    creds = Credentials(**st.session_state['credentials'])
    service = build('drive', 'v3', credentials=creds)

    # Função para listar arquivos
    def listar_arquivos(folder_id=None):
        query = "'root' in parents and trashed = false" if not folder_id else f"'{folder_id}' in parents and trashed = false"
        results = service.files().list(q=query,
                                       fields="files(id, name, mimeType, modifiedTime, size, webViewLink)").execute()
        items = results.get('files', [])
        return items

    st.info('🔎 Lendo seus arquivos do Google Drive...')
    arquivos = listar_arquivos()

    if arquivos:
        data = []
        for item in arquivos:
            data.append({
                'Nome': item['name'],
                'Tipo': 'Pasta' if item['mimeType'] == 'application/vnd.google-apps.folder' else 'Arquivo',
                'MIME': item['mimeType'],
                'Link': item['webViewLink'],
                'Última Modificação': item['modifiedTime'],
                'Tamanho': item.get('size', '—')
            })
        df = pd.DataFrame(data)
        st.write('### 📋 Arquivos Encontrados:', df)

        # Filtros Dinâmicos
        filtro_tipo = st.multiselect('Filtrar por Tipo', df['Tipo'].unique())
        if filtro_tipo:
            df = df[df['Tipo'].isin(filtro_tipo)]

        # Download XLSX
        excel = df.to_excel(index=False, engine='openpyxl')
        st.download_button(
            label="📥 Baixar XLSX",
            data=excel,
            file_name='extrato_google_drive.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        st.warning('Nenhum arquivo encontrado.')
