import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

# α (Alfa) - Organização segura das credenciais
st.title("📂 Lista de Arquivos do Google Drive")

# Configuração do Google OAuth com Service Account (deve ser configurado no Streamlit Secrets)
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=["https://www.googleapis.com/auth/drive.readonly"],
)

# β (Beta) - Função modular para listar arquivos
@st.cache_data
def listar_arquivos():
    try:
        service = build('drive', 'v3', credentials=creds)
        arquivos = []
        pagina_token = None
        while True:
            resposta = service.files().list(
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, modifiedTime, webViewLink)",
                pageToken=pagina_token
            ).execute()
            for arquivo in resposta.get('files', []):
                arquivos.append({
                    "Nome": arquivo.get('name'),
                    "ID": arquivo.get('id'),
                    "Tipo": arquivo.get('mimeType'),
                    "Última Modificação": arquivo.get('modifiedTime'),
                    "Link": arquivo.get('webViewLink')
                })
            pagina_token = resposta.get('nextPageToken', None)
            if not pagina_token:
                break
        return arquivos
    except Exception as e:
        st.error(f"Erro ao listar arquivos: {e}")
        return []

# Botão para iniciar
if st.button("🔍 Listar Arquivos"):
    # γ (Gama) - Chamada segura da API
    arquivos = listar_arquivos()
    if arquivos:
        df = pd.DataFrame(arquivos)
        st.dataframe(df)

        # ε (Epsilon) - Exportação para XLS
        xls = df.to_excel(index=False, engine='openpyxl')
        st.download_button("📥 Download XLS", data=xls, file_name='lista_arquivos.xlsx')
    else:
        st.warning("Nenhum arquivo encontrado ou erro na API.")
