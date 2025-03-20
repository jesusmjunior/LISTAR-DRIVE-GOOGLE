import streamlit as st
from html.parser import HTMLParser
import pandas as pd

# CONFIGURAÇÃO STREAMLIT
st.set_page_config(page_title="🔎 Scraping Google Drive ou HTML", layout="centered")
st.title("📂 Google Drive Scraper - Sem BeautifulSoup")

st.markdown("""
## 👋 Bem-vindo!

Este app faz scraping de HTML simples SEM usar BeautifulSoup (sem instalação extra).

Cole abaixo qualquer HTML ou resultado que deseja parsear.
""")

# DEFININDO PARSER NATIVO
class MeuParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.textos = []
        self.links = []

    def handle_data(self, data):
        texto = data.strip()
        if texto:
            self.textos.append(texto)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    self.links.append(attr[1])

# INPUT DO USUÁRIO
html_input = st.text_area("📥 Cole aqui o HTML:", "<h1>Título</h1><p>Parágrafo de exemplo.</p><a href='https://google.com'>Google</a>")

if st.button("🔍 Fazer Scraping"):
    parser = MeuParser()
    parser.feed(html_input)
    
    st.subheader("🎯 Textos Extraídos:")
    for texto in parser.textos:
        st.write(f"- {texto}")
    
    st.subheader("🔗 Links Encontrados:")
    for link in parser.links:
        st.write(f"- {link}")
    
    # EXPORTAR PARA XLS
    if parser.textos or parser.links:
        df = pd.DataFrame({
            "Textos": parser.textos,
            "Links": parser.links + [""]*(len(parser.textos) - len(parser.links)) if len(parser.links) < len(parser.textos) else parser.links
        })
        st.download_button("📥 Baixar XLS", df.to_csv(index=False), file_name="resultado_scraping.csv")
