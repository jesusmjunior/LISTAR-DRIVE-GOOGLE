import streamlit as st
import pandas as pd
import re

# =========================
# CONFIGURAÇÃO DO APP
# =========================
st.set_page_config(page_title="📊 Dashboard CSV - Adm. Jesus Martins", layout="wide")
st.title("📊 Dashboard CSV - Adm. Jesus Martins")

st.markdown("""
## 📥 Faça upload até 3 arquivos CSV e veja tudo combinado!

- Tabelas interativas com filtros.
- Gráficos simples.
- Links clicáveis diretos.

---
""")

# =========================
# UPLOAD DOS CSVs
# =========================
uploaded_files = st.file_uploader("📂 Faça upload de até 3 arquivos CSV:", accept_multiple_files=True, type=['csv'])

dfs = []
if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} arquivos carregados!")
    for file in uploaded_files:
        df = pd.read_csv(file)
        st.write(f"### 📄 Visualizando: `{file.name}`")
        st.dataframe(df)
        dfs.append(df)

    # =========================
    # COMBINAÇÃO DOS CSVs
    # =========================
    combined_df = pd.concat(dfs, ignore_index=True, sort=False)
    st.write("## 🔗 Dados Combinados:")

    # Links clicáveis
    def make_clickable(val):
        if isinstance(val, str) and ('http' in val or 'https' in val):
            return f'<a href="{val}" target="_blank">🔗 Link</a>'
        return val

    st.write(combined_df.style.format(make_clickable).to_html(escape=False), unsafe_allow_html=True)

    # =========================
    # FILTROS DINÂMICOS
    # =========================
    st.sidebar.header("Filtros Dinâmicos:")
    for col in combined_df.columns:
        if combined_df[col].nunique() < 50 and combined_df[col].dtype == 'object':
            options = st.sidebar.multiselect(f"Filtrar {col}:", combined_df[col].unique())
            if options:
                combined_df = combined_df[combined_df[col].isin(options)]

    # =========================
    # TABELA FILTRADA
    # =========================
    st.write("## 📋 Tabela Filtrada:")
    st.dataframe(combined_df)

    # =========================
    # GRÁFICO SIMPLES
    # =========================
    st.write("## 📊 Gráfico Simples:")

    numeric_cols = combined_df.select_dtypes(include=['float64', 'int64']).columns
    if len(numeric_cols) >= 1:
        col_y = st.selectbox("Selecione a coluna para gráfico:", numeric_cols)
        st.bar_chart(combined_df[col_y])
    else:
        st.info("Nenhuma coluna numérica encontrada para gerar gráfico.")

else:
    st.info("🔽 Faça upload dos arquivos CSV acima para começar!")
