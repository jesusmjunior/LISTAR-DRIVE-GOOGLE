import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="📂 Scraping Google Drive Público", layout="centered")
st.title("📂 Leitor de Pasta Google Drive Pública")

url = st.text_input("🔗 Insira o link público da pasta do Google Drive:")

if url:
    st.markdown("✅ Pasta carregada abaixo. Clique para extrair os nomes dos arquivos e pastas visíveis.")
    
    # Iframe para renderizar a pasta pública
    components.iframe(url, height=600, scrolling=True)
    
    # JavaScript para capturar DOM (simples para o usuário executar no browser)
    st.markdown("""
    <script>
    function extrairDrive() {
        let itens = document.querySelectorAll('div[role="gridcell"], span, a');  // Padrões usados no Drive
        let resultado = "";
        itens.forEach(el => {
            if (el.innerText) {
                resultado += el.innerText + "\\n";
            }
        });
        const txtBox = window.parent.document.querySelector('textarea[data-testid="stTextArea"]');
        txtBox.value = resultado;
    }
    </script>
    <button onclick="extrairDrive()">📥 Extrair Nomes & Textos do Google Drive</button>
    """, unsafe_allow_html=True)
    
    texto_extraido = st.text_area("📄 Texto Extraído:", height=400)
    
    if texto_extraido:
        st.download_button("📥 Baixar Texto", texto_extraido, file_name="google_drive_extracao.txt")
