import streamlit as st
import pandas as pd
import requests
import re

# =========================
# CONFIGURAÇÃO DO DASHBOARD
# =========================
st.set_page_config(page_title="📊 Dashboard DRMs Google Sheets 2025", layout="wide")
st.title("📊 Painel Consolidado de DRMs - Dados Públicos 2025")

# =========================
# GOOGLE SHEETS CONFIGURAÇÃO
# =========================
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSMDcKkFLItxGY0Kb9QBkeQAaYGXYczh0rn7w7bmvQjfSwwCpfo9lNowR4XIPiYNtL4RdGXDUq8NEht/pub?gid=1916790160&single=true&output=csv"
API_KEY = "AIzaSyAKibc0A3TerDdfQeZBLePxU01PbK_53Lw"

# =========================
# LEITURA DIRETA DO CSV PÚBLICO
# =========================
@st.cache_data
def load_csv_sheet():
    df_estrutura = pd.read_csv(CSV_URL)
    return df_estrutura

# =========================
# CARREGANDO OS DADOS DO GOOGLE SHEETS
# =========================
df_estrutura = load_csv_sheet()

st.success("✅ Dados carregados com sucesso!")

# =========================
# EXIBIR A MEDALHA E ÍCONES DINÂMICOS
# =========================
total_drm = df_estrutura[df_estrutura['Nome_Arquivo'].str.contains('DRM')].shape[0]
st.markdown(f"🎉 **Total de DRMs encontrados:** {total_drm}")

# =========================
# EXIBIR TABELA FILTRADA COM DECOMPOSIÇÃO DO NOME DO ARQUIVO
# =========================
df_estrutura['Categoria'] = df_estrutura['Nome_Arquivo'].apply(lambda x: 'DRM' if 'DRM' in x else ('DECISÃO' if 'DECISÃO' in x else ('DECLARAÇÃO' if 'DECLARAÇÃO' in x else ('MINUTA' if 'MINUTA' in x else 'OUTRO'))))

# Melhorando extração do município, mês e ano
df_estrutura['Município'] = df_estrutura['Path'].apply(lambda x: x.split('/')[-1])
df_estrutura['Mês'] = df_estrutura['Nome_Arquivo'].apply(lambda x: re.search(r'(\d{2})', x).group(1) if re.search(r'(\d{2})', x) else '')
df_estrutura['Ano'] = df_estrutura['Nome_Arquivo'].apply(lambda x: x.split('-')[2] if len(x.split('-')) > 2 else '')
df_estrutura['Mês_Entrega'] = df_estrutura['Nome_Arquivo'].apply(lambda x: 'Janeiro' if '01' in x else ('Fevereiro' if '02' in x else 'Outro'))

# =========================
# EXIBIR TABELA COM CATEGORIAS E DADOS
# =========================
st.subheader("📂 Estrutura das Pastas e Arquivos - Categorizados por Nome de Arquivo")

# Exibir os dados com filtro por coluna
st.write("🔎 **Filtragem de dados**")
filtro_nome = st.text_input("🔍 Filtrar por nome do arquivo DRM:", "")

# Filtrando os dados conforme o nome
df_filtrado = df_estrutura[df_estrutura['Nome_Arquivo'].str.contains(filtro_nome, case=False)]

# Exibir a tabela filtrada
st.dataframe(df_filtrado[['Nome_Arquivo', 'Categoria', 'Município', 'Mês_Entrega', 'Mês', 'Ano', 'Link']])

# =========================
# GRÁFICOS: CATEGORIAS E NÚMEROS
# =========================
st.subheader("📊 Gráfico: Distribuição por Categoria")

# Gráfico de Distribuição por Categoria
categoria_count = df_filtrado['Categoria'].value_counts()
st.bar_chart(categoria_count)

# Gráfico de Distribuição por Mês de Entrega
st.subheader("📊 Gráfico: Distribuição de Arquivos por Mês de Entrega")
mes_entrega_count = df_filtrado['Mês_Entrega'].value_counts()
st.bar_chart(mes_entrega_count)

# =========================
# FUNÇÃO DE SANITIZAÇÃO DOS DADOS DO PDF
# =========================
def sanitizar_drm_texto(texto):
    dados = {}
    dados['Código Serventia'] = re.search(r'Código da Serventia\s*:?\s*(\d+)', texto)
    dados['Receita Bruta'] = re.search(r'TOTAL DA RECEITA BRUTA\s*R\$\s*([\d\.,]+)', texto)
    dados['Despesa Total'] = re.search(r'TOTAL DESPESAS\s*R\$\s*([\d\.,]+)', texto)
    dados['Saldo a Devolver'] = re.search(r'SALDO A DEVOLVER\s*R\$\s*([\d\.,]+)', texto)
    dados['Teto Constitucional'] = re.search(r'TETO CONSTITUCIONAL\s*R\$\s*([\d\.,]+)', texto)
    dados['Período'] = re.search(r'Per[ií]odo\s*:?\s*(.*?)\s*M[eê]s', texto)
    for key in dados:
        dados[key] = dados[key].group(1).strip() if dados[key] else ''
    return dados

# =========================
# TABELA DE SANITIZAÇÃO COM DADOS DO PDF
# =========================
painel_virtual = []

for index, row in df_filtrado[df_filtrado['Categoria'] == 'DRM'].iterrows():
    st.write(f"**📄 {row['Nome_Arquivo']}**")
    st.write(f"📁 Path: {row['Path']} | 🗓️ Tipo: {row['Categoria']} | 📅 Entrega: {row['Mês_Entrega']}")
    st.markdown(f"[Abrir Link]({row['Link']})", unsafe_allow_html=True)
    try:
        response = requests.get(row['Link'])
        texto_extraido = response.content.decode('latin1', errors='ignore')
        dados_sanitizados = sanitizar_drm_texto(texto_extraido)
        st.json(dados_sanitizados)
        painel_virtual.append({
            "Nome_Arquivo": row['Nome_Arquivo'],
            "Path": row['Path'],
            "Categoria": row['Categoria'],
            "Mês_Entrega": row['Mês_Entrega'],
            "Mês": row['Mês'],
            "Ano": row['Ano'],
            **dados_sanitizados
        })
    except Exception as e:
        st.error(f"Erro ao sanitizar dados: {e}")

# =========================
# DOWNLOAD DOS DADOS SANITIZADOS
# =========================
if painel_virtual:
    df_virtual = pd.DataFrame(painel_virtual)
    st.subheader("📑 Banco Virtual Sanitizado Consolidado")
    st.dataframe(df_virtual)
    csv_virtual = df_virtual.to_csv(index=False)
    st.download_button("📥 Baixar Banco Virtual Sanitizado CSV", csv_virtual, file_name="banco_virtual_DRM_sanitizado.csv")
