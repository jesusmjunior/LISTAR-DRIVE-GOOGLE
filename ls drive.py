import streamlit as st
import pandas as pd
import requests

# --- CONFIGURAÇÕES BÁSICAS ---
st.set_page_config(page_title="Adm. Jesus Martins - Extratador de dados do Google Drive", page_icon="📂")

st.title('📂 Adm. Jesus Martins - Extratador de dados do Google Drive')

st.write("""
Faça login com sua conta Google, autorize o acesso, e gere um relatório do seu Google Drive.
""")

# --- PARÂMETROS DO CLIENT_ID (público) ---
CLIENT_ID = "YOUR_PUBLIC_CLIENT_ID.apps.googleusercontent.com"  # Substitua pelo seu Client ID do Google
REDIRECT_URI = "https://YOUR-STREAMLIT-APP.streamlit.app"  # Substitua pelo seu Streamlit URL
SCOPE = "https://www.googleapis.com/auth/drive.metadata.readonly"
RESPONSE_TYPE = "token"

# --- LINK OAUTH GOOGLE ---
oauth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type={RESPONSE_TYPE}&scope={SCOPE}&include_granted_scopes=true"

st.markdown(f"### 🔑 [Clique aqui para fazer login com Google e autorizar acesso]({oauth_url})")

# --- CAPTURA TOKEN VIA URL ---
token = st.experimental_get_query_params().get("access_token", [None])[0]

if token:
    st.success("✅ Autorizado com sucesso! Gerando relatório...")

    # --- CONSULTA DIRETA À API GOOGLE DRIVE ---
    headers = {"Authorization": f"Bearer {token}"}
    params = {"pageSize": 1000, "fields": "files(id, name, mimeType, modifiedTime, size, webViewLink)"}
    response = requests.get("https://www.googleapis.com/drive/v3/files", headers=headers, params=params)

    if response.status_code == 200:
        files = response.json().get("files", [])
        if files:
            # --- TRANSFORMAR EM DATAFRAME ---
            df = pd.DataFrame([{
                "Nome": f["name"],
                "Tipo": "Pasta" if f["mimeType"] == "application/vnd.google-apps.folder" else "Arquivo",
                "MIME": f["mimeType"],
                "Link": f.get("webViewLink", ""),
                "Última Modificação": f.get("modifiedTime", ""),
                "Tamanho (Bytes)": f.get("size", "—")
            } for f in files])

            st.write("### 📋 Arquivos encontrados:")
            st.dataframe(df)

            # --- FILTROS DINÂMICOS ---
            tipo_filter = st.multiselect('Filtrar por Tipo', df['Tipo'].unique())
            if tipo_filter:
                df = df[df['Tipo'].isin(tipo_filter)]

            # --- DOWNLOAD XLSX ---
            excel_bytes = df.to_excel(index=False, engine='openpyxl')
            st.download_button(
                label="📥 Baixar XLSX",
                data=excel_bytes,
                file_name='extrato_google_drive.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            st.warning("Nenhum arquivo encontrado.")
    else:
        st.error("Erro ao consultar Google Drive API.")
else:
    st.warning("⚠️ Faça login para continuar.")
