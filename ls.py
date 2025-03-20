import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Configuração da página
st.set_page_config(page_title="📂 Google Drive - Pasta Pública", layout="centered")

# Título e instruções
st.title("📂 Google Drive - Listar Arquivos de Pasta Pública")

st.markdown("""
### 🚀 Como usar:
1️⃣ Copie e cole abaixo o link público da pasta do Google Drive.  
2️⃣ O sistema listará todos os arquivos disponíveis.  
3️⃣ Você poderá baixar a lista em XLS.

⚠️ **Importante:** A pasta precisa estar configurada como **"Qualquer pessoa com link pode visualizar".**
""")

# Input do link da pasta pública
link = st.text_input("🔗 Insira o link da pasta pública do Google Drive:")

# Função para extrair arquivos da pasta
def extrair_arquivos_pasta(link_pasta):
    arquivos = []
    try:
        response = requests.get(link_pasta)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Busca por divs com IDs dos arquivos
        for tag in soup.find_all('div'):
            if 'data-id' in tag.attrs:
                file_id = tag['data-id']
                nome_arquivo = tag.text.strip()
                link_download = f"https://drive.google.com/uc?id={file_id}&export=download"
                arquivos.append({
                    'Nome do Arquivo': nome_arquivo,
                    'ID do Arquivo': file_id,
                    'Link Download Direto': link_download
                })
        return pd.DataFrame(arquivos)
    except Exception as e:
        return f"Erro ao acessar: {e}"

# Processamento quando o usuário insere o link
if link:
    with st.spinner("🔄 Buscando arquivos na pasta..."):
        resultado = extrair_arquivos_pasta(link)
        if isinstance(resultado, pd.DataFrame) and not resultado.empty:
            st.success(f"✅ {len(resultado)} arquivos encontrados!")
            st.dataframe(resultado)

            # Botão para exportação XLS
            xls = resultado.to_excel(index=False, engine='openpyxl')
            st.download_button(
                label="📥 Baixar Lista de Arquivos em XLS",
                data=xls,
                file_name="lista_arquivos_drive.xlsx"
            )
        else:
            st.error("❌ Não foi possível localizar arquivos. Verifique se o link está correto e a pasta está pública.")
