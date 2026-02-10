import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Gestão Pro v4.2", layout="wide")

st.title("🚀 Gestão Pro v4.2")
st.sidebar.header("Painel de Controle")

# Simulação de Banco de Dados Simples
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=['Cliente', 'CNJ', 'Operador', 'Retorno', 'Status'])

menu = st.sidebar.selectbox("Ir para:", ["Dashboard", "Meus Clientes", "Admin (Importar/Girar)"])

if menu == "Dashboard":
    st.write("### Visão Geral da Carteira")
    st.info("O sistema está online e aguardando dados.")
    
elif menu == "Admin (Importar/Girar)":
    senha = st.text_input("Senha Admin", type="password")
    if senha == "admin123":
        st.success("Acesso Liberado")
        # Aqui entrará a lógica da Missão 02
    elif senha != "":
        st.error("Senha Incorreta")

st.write("---")
st.caption(f"Acessado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
