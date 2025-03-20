import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Configuração da página
st.set_page_config(page_title="📂 Google Drive - Pasta Pública", layout="centered")

# Título e instruções minimalistas
st.title("📂 Google Drive - Listar Arquivos")

st.markdown("""
1️⃣ Cole abaixo o link público da pasta do Google Drive.  
2️⃣ O app listará os arquivos disponíveis, com link direto para download.  
3️⃣ Você pode exportar a lista em XLS.
""")

# Input do link
link = st.text_input("🔗 Link da pasta pública do Google Drive:")

# Função para extrair arquivos da pasta
def listar_arquivos_pasta(link_pasta):
    arquivos = []
    try:
        response = requests.get(link_pasta)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extração baseada na estrutura pública do Google Drive
        for tag in soup.find_all('div'):
            if 'data-id' in tag.attrs:
                file_id = tag['data-id']
                nome_arquivo = tag.text.strip()
                link_download = f"https://drive.google.com/uc?id={file_id}&export=download"
                arquivos.append({
                    'Nome do Arquivo': nome_arquivo,
                    'ID do Arquivo': file_id,
                    'Link Direto': link_download
                })
        return pd.DataFrame(arquivos)
    except Exception as e:
        return f"Erro ao acessar: {e}"

# Execução principal
if link:
    with st.spinner("🔄 Buscando arquivos..."):
        resultado = listar_arquivos_pasta(link)
        if isinstance(resultado, pd.DataFrame) and not resultado.empty:
            st.success(f"✅ {len(resultado)} arquivos encontrados!")
            st.dataframe(resultado)

            # Exportação XLS
            xls = resultado.to_excel(index=False, engine='openpyxl')
            st.download_button(
                label="📥 Baixar lista em XLS",
                data=xls,
                file_name="lista_arquivos_drive.xlsx"
            )
        else:
            st.error("❌ Não foi possível localizar arquivos. Verifique se o link é público.")
