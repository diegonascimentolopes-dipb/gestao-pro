import streamlit as st
import pandas as pd
from datetime import datetime, date
import re
import numpy as np

# 1. Configuração e Estado
st.set_page_config(page_title="Gestão Pro v4.2", layout="wide", initial_sidebar_state="collapsed")

if 'clientes' not in st.session_state:
    st.session_state.clientes = pd.DataFrame(columns=['Cliente', 'CNJ', 'Operador', 'Status', 'Last_Touch', 'Retorno'])

if 'operadores' not in st.session_state:
    st.session_state.operadores = ["Operador Padrão"]

# --- FUNÇÕES CORE ---

def aplicar_mascara_cnj(texto):
    padrao = r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}'
    resultado = re.findall(padrao, texto)
    return resultado[0] if resultado else "0000000-00.0000.0.00.0000"

def girar_carteira():
    if st.session_state.clientes.empty or len(st.session_state.operadores) == 0:
        return
    
    df = st.session_state.clientes.copy()
    ops = st.session_state.operadores.copy()
    
    # Shuffle (Embaralhamento)
    df = df.sample(frac=1).reset_index(drop=True)
    
    # Distribuição Equitativa
    n_ops = len(ops)
    for i in range(len(df)):
        df.at[i, 'Operador'] = ops[i % n_ops]
    
    st.session_state.clientes = df
    st.success("🔄 Giro de Carteira concluído com sucesso!")

def colorir_tabela(val):
    hoje = date.today()
    try:
        data_ret = datetime.strptime(val, '%Y-%m-%d').date()
        if data_ret < hoje:
            return 'background-color: #fee2e2; color: #991b1b' # Vermelho (Atrasado)
        elif data_ret == hoje:
            return 'background-color: #fef9c3; color: #854d0e' # Amarelo (Hoje)
        else:
            return 'background-color: #dcfce7; color: #166534' # Verde (Agendado)
    except:
        return ''

# --- INTERFACE ---

st.title("🚀 Gestão Pro v4.2")

tabs = st.tabs(["📊 Dashboard", "👤 Meus Clientes", "🔐 Admin"])

with tabs[0]:
    st.header("Resumo Estratégico")
    
    if not st.session_state.clientes.empty:
        # Cálculo de Inatividade
        df_view = st.session_state.clientes.copy()
        # Aplicar estilização visual
        st.write("### Carteira Geral (Monitoramento de Prazos)")
        st.dataframe(df_view.style.applymap(colorir_tabela, subset=['Retorno']), use_container_width=True)
    else:
        st.info("Nenhum dado disponível. Vá para a aba Admin para importar.")

with tabs[1]:
    st.header("👤 Minha Operação")
    op_escolhido = st.selectbox("Selecione seu nome:", st.session_state.operadores)
    
    # Filtro de clientes do operador
    meus_clientes = st.session_state.clientes[st.session_state.clientes['Operador'] == op_escolhido]
    
    if not meus_clientes.empty:
        st.write(f"Sua carteira possui **{len(meus_clientes)}** clientes.")
        # Permitir edição rápida de status e data (Simulado)
        edited_df = st.data_editor(meus_clientes, use_container_width=True)
        if st.button("Salvar Alterações"):
            st.session_state.clientes.update(edited_df)
            st.toast("Progresso salvo!")
    else:
        st.warning("Você não possui clientes atribuídos. Solicite ao Admin para realizar o 'Giro'.")

with tabs[2]:
    st.header("🔐 Painel de Controle")
    senha = st.text_input("Senha Mestre", type="password")
    
    if senha == "admin123":
        st.success("Modo Gestor Ativado")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Giro de Carteira")
            if st.button("🌀 EXECUTAR GIRO AGORA"):
                girar_carteira()
                st.rerun()
        
        with col2:
            st.subheader("Equipe")
            novo_op = st.text_input("Novo Operador")
            if st.button("Adicionar"):
                st.session_state.operadores.append(novo_op)
                st.rerun()

        st.divider()
        st.subheader("📥 Importação Bruta")
        texto = st.text_area("Cole os dados aqui")
        if st.button("Importar"):
            # Lógica de importação simplificada da Missão 02
            linhas = [l for l in texto.split('\n') if l.strip()]
            novos = []
            for l in linhas:
                cnj = aplicar_mascara_cnj(l)
                novos.append({'Cliente': l[:20], 'CNJ': cnj, 'Operador': 'Não Atribuído', 
                              'Status': 'Novo', 'Last_Touch': str(date.today()), 'Retorno': str(date.today())})
            st.session_state.clientes = pd.concat([st.session_state.clientes, pd.DataFrame(novos)], ignore_index=True)
            st.rerun()

st.caption(f"Gestão Pro v4.2 | Desenvolvido para Diego")
