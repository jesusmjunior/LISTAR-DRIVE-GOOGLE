import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="📂 Google Drive Pasta Pública", layout="centered")
st.title("📂 Google Drive - Listar Arquivos de Pasta Pública")

st.markdown("""
### 🚀 Insira abaixo o link da pasta pública do Google Drive:

⚠️ **Importante:** A pasta deve estar com permissão **"Qualquer pessoa com link pode visualizar".  
O sistema listará os arquivos disponíveis com seus respectivos links.**
""")

link = st.text_input("🔗 Link da pasta pública:")

def extrair_arquivos_pasta(link_pasta):
    arquivos = []
    try:
        response = requests.get(link_pasta)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Busca por IDs dos arquivos na página
        for tag in soup.find_all('div'):
            if 'data-id' in tag.attrs:
                file_id = tag['data-id']
                nome_arquivo = tag.text.strip()
                link_download = f"https://drive.google.com/uc?id={file_id}&export=download"
                arquivos.append({
                    'Nome do Arquivo': nome_arquivo,
                    'ID': file_id,
                    'Link Download Direto': link_download
                })
        return pd.DataFrame(arquivos)
    except Exception as e:
        return f"Erro ao acessar: {e}"

if link:
    with st.spinner("🔄 Buscando arquivos na pasta..."):
        resultado = extrair_arquivos_pasta(link)
        if isinstance(resultado, pd.DataFrame) and not resultado.empty:
            st.success(f"✅ {len(resultado)} arquivos encontrados!")
            st.dataframe(resultado)

            # Download XLS
            st.download_button(
                "📥 Baixar Lista de Arquivos em XLS",
                resultado.to_excel(index=False),
                file_name="lista_arquivos_drive.xlsx"
            )
        else:
            st.error("❌ Não foi possível localizar arquivos. Verifique se o link está correto e é público.")
