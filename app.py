import streamlit as st
import pandas as pd
from datetime import datetime
import re

# 1. Configuração e Estado do Sistema (Simulando Banco de Dados)
st.set_page_config(page_title="Gestão Pro v4.2", layout="wide", initial_sidebar_state="collapsed")

if 'clientes' not in st.session_state:
    st.session_state.clientes = pd.DataFrame(columns=['Cliente', 'CNJ', 'Operador', 'Status', 'Last_Touch', 'Retorno'])

if 'operadores' not in st.session_state:
    st.session_state.operadores = ["Operador Padrão"]

# Funções Auxiliares
def aplicar_mascara_cnj(texto):
    padrao = r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}'
    resultado = re.findall(padrao, texto)
    return resultado[0] if resultado else "0000000-00.0000.0.00.0000"

# --- INTERFACE ---
st.title("🚀 Gestão Pro v4.2")

tabs = st.tabs(["📊 Dashboard", "👤 Meus Clientes", "🔐 Admin"])

with tabs[0]:
    st.header("Resumo Geral")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Clientes", len(st.session_state.clientes))
    col2.metric("Operadores Ativos", len(st.session_state.operadores))
    col3.metric("Aguardando Giro", len(st.session_state.clientes[st.session_state.clientes['Operador'] == 'Não Atribuído']))
    
    if not st.session_state.clientes.empty:
        st.dataframe(st.session_state.clientes, use_container_width=True)
    else:
        st.info("Nenhum dado para exibir. Vá em Admin.")

with tabs[1]:
    st.header("👤 Minha Carteira")
    op_escolhido = st.selectbox("Identifique-se:", st.session_state.operadores)
    meus_dados = st.session_state.clientes[st.session_state.clientes['Operador'] == op_escolhido]
    
    if not meus_dados.empty:
        st.table(meus_dados)
    else:
        st.warning(f"Não há clientes atribuídos para {op_escolhido}.")

with tabs[2]:
    st.header("🔐 Painel de Controle (Admin)")
    senha = st.text_input("Senha Mestre", type="password")
    
    if senha == "admin123":
        st.success("Acesso Liberado!")
        
        # --- SUB-ABA: GESTÃO DE EQUIPE ---
        with st.expander("👥 Gerenciar Equipe"):
            novo_op = st.text_input("Nome do Novo Operador")
            if st.button("Adicionar Operador"):
                if novo_op and novo_op not in st.session_state.operadores:
                    st.session_state.operadores.append(novo_op)
                    st.toast(f"{novo_op} adicionado!")
            st.write("Operadores atuais:", st.session_state.operadores)

        # --- SUB-ABA: IMPORTAÇÃO ---
        with st.expander("📥 Importar Novos Clientes"):
            st.write("Cole a lista de nomes e/ou números de processo abaixo:")
            texto_bruto = st.text_area("Lista de Importação", placeholder="Ex: João Silva 0001234-55.2023.8.11.0001")
            
            if st.button("Processar e Adicionar"):
                linhas = texto_bruto.split('\n')
                novos_registros = []
                for linha in linhas:
                    if linha.strip():
                        cnj = aplicar_mascara_cnj(linha)
                        nome = linha.replace(cnj, "").strip() if cnj != "0000000-00.0000.0.00.0000" else linha.strip()
                        novos_registros.append({
                            'Cliente': nome,
                            'CNJ': cnj,
                            'Operador': 'Não Atribuído',
                            'Status': 'Novo',
                            'Last_Touch': datetime.now().strftime('%Y-%m-%d'),
                            'Retorno': datetime.now().strftime('%Y-%m-%d')
                        })
                
                df_novos = pd.DataFrame(novos_registros)
                st.session_state.clientes = pd.concat([st.session_state.clientes, df_novos], ignore_index=True)
                st.success(f"{len(df_novos)} clientes importados com sucesso!")

        if st.button("⚠️ Resetar Tudo"):
            st.session_state.clientes = pd.DataFrame(columns=['Cliente', 'CNJ', 'Operador', 'Status', 'Last_Touch', 'Retorno'])
            st.rerun()

    elif senha != "":
        st.error("Senha incorreta.")

st.divider()
st.caption(f"Gestão Pro v4.2 | Diego Nascimento Lopes")
