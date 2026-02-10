import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuração de Página e Estilo para Navegação Superior
st.set_page_config(page_title="Gestão Pro v4.2", layout="wide")

# CSS para esconder a barra lateral e estilizar botões superiores
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-nav {display: flex; gap: 10px; margin-bottom: 20px;}
    </style>
""", unsafe_content_html=True)

st.title("🚀 Gestão Pro v4.2")

# 2. Navegação por abas na parte superior
tabs = st.tabs(["📊 Dashboard", "👤 Meus Clientes", "🔐 Admin"])

with tabs[0]:
    st.header("Visão Geral")
    st.info("O banco de dados está vazio. Vá em 'Admin' para importar novos clientes.")

with tabs[1]:
    st.header("Meus Clientes")
    operador = st.selectbox("Selecione seu nome:", ["Aguardando Importação..."])
    st.warning("Nenhum dado vinculado ao seu operador ainda.")

with tabs[2]:
    st.header("Área Restrita")
    senha = st.text_input("Digite a Senha Mestre", type="password")
    
    if senha == "admin123":
        st.success("Acesso Liberado!")
        st.subheader("Configurações do Gestor")
        # Espaço para o Motor de Importação da Missão 02
        st.button("Limpar Base de Dados (Reset)")
    elif senha != "":
        st.error("Senha incorreta.")

st.write("---")
st.caption(f"Gestão Pro v4.2 | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
