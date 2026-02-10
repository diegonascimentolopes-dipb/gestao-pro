import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuração de Página (O Streamlit cria a navegação superior automaticamente com st.tabs)
st.set_page_config(page_title="Gestão Pro v4.2", layout="wide", initial_sidebar_state="collapsed")

# Título Principal
st.title("🚀 Gestão Pro v4.2")

# 2. Navegação por abas (Menu Superior)
tabs = st.tabs(["📊 Dashboard", "👤 Meus Clientes", "🔐 Admin"])

with tabs[0]:
    st.header("Visão Geral")
    st.info("O banco de dados está vazio. Vá em 'Admin' para importar novos clientes.")

with tabs[1]:
    st.header("Meus Clientes")
    # Seletor de operador simplificado
    operador = st.selectbox("Operador Atual:", ["Aguardando Importação..."])
    st.warning("Nenhum dado vinculado ao seu operador ainda.")

with tabs[2]:
    st.header("Área Restrita")
    # Uso de colunas para organizar o login
    col1, col2 = st.columns([1, 2])
    with col1:
        senha = st.text_input("Senha Mestre", type="password")
    
    if senha == "admin123":
        st.success("Acesso Liberado!")
        st.divider()
        st.subheader("🛠️ Painel do Gestor")
        st.info("Pronto para iniciar a Missão 02: Importação de Dados.")
    elif senha != "":
        st.error("Senha incorreta.")

# Rodapé simples
st.divider()
st.caption(f"Gestão Pro v4.2 | Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
