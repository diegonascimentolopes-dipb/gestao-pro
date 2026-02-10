import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuração de Página
st.set_page_config(page_title="Gestão Pro v4.2", layout="wide")

# 2. Estilização CSS Corrigida
st.markdown("""
<style>
    /* Remove a barra lateral */
    [data-testid="stSidebar"] {display: none;}
    /* Ajusta o espaçamento do topo */
    .block-container {padding-top: 2rem;}
</style>
""", unsafe_content_html=True)

st.title("🚀 Gestão Pro v4.2")

# 3. Navegação por abas (Menu Superior)
tabs = st.tabs(["📊 Dashboard", "👤 Meus Clientes", "🔐 Admin"])

with tabs[0]:
    st.header("Visão Geral")
    st.info("O banco de dados está vazio. Vá em 'Admin' para importar novos clientes.")

with tabs[1]:
    st.header("Meus Clientes")
    st.write("Selecione seu nome para visualizar sua carteira.")
    operador = st.selectbox("Operador Atual:", ["Aguardando Importação..."], label_visibility="collapsed")
    st.warning("Nenhum dado vinculado ao seu operador ainda.")

with tabs[2]:
    st.header("Área Restrita")
    senha = st.text_input("Digite a Senha Mestre", type="password")
    
    if senha == "admin123":
        st.success("Acesso Liberado!")
        st.subheader("Configurações do Gestor")
        # Botão de Reset (estaremos salvando dados em Missões futuras)
        if st.button("Limpar Base de Dados (Reset)"):
            st.warning("Função de limpeza será ativada na Missão 02.")
    elif senha != "":
        st.error("Senha incorreta.")

st.write("---")
st.caption(f"Gestão Pro v4.2 | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
