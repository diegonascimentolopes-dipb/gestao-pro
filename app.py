import streamlit as st
import pandas as pd
from datetime import datetime, date
import re

# 1. CONFIGURAÇÃO NATIVA (Sem CSS externo para evitar erros)
st.set_page_config(
    page_title="Gestão Pro v4.2", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 2. INICIALIZAÇÃO DO BANCO (SESSION STATE)
if 'clientes' not in st.session_state:
    st.session_state.clientes = pd.DataFrame(columns=['id', 'Cliente', 'CNJ', 'Operador', 'Status', 'Data_Retorno'])

if 'operadores' not in st.session_state:
    st.session_state.operadores = ["Diego", "Samara", "Natan"]

# 3. FUNÇÕES LÓGICAS
def normalizar_id(texto):
    return re.sub(r'[^A-Z0-9]', '', str(texto).upper())

def extrair_cnj(texto):
    padrao = r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}'
    resultado = re.findall(padrao, texto)
    return resultado[0] if resultado else "Sem Processo"

# 4. INTERFACE
st.title("🚀 Gestão Pro v4.2")

# Navegação por Abas Superiores
tabs = st.tabs(["📊 DASHBOARD", "👤 MEUS CLIENTES", "🛠️ ADMIN"])

# --- ABA 1: DASHBOARD ---
with tabs[0]:
    st.subheader("Indicadores de Desempenho")
    df = st.session_state.clientes
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total de Clientes", len(df))
    m2.metric("Operadores Ativos", len(st.session_state.operadores))
    
    if not df.empty:
        try:
            df['dt_temp'] = pd.to_datetime(df['Data_Retorno'], format='%d/%m/%Y').dt.date
            atrasados = len(df[df['dt_temp'] < date.today()])
            m3.metric("🚨 Prazos Atrasados", atrasados)
        except:
            m3.metric("🚨 Prazos Atrasados", "Erro data")
    
    st.info("Consulte a aba 'Meus Clientes' para gerenciar seus processos.")

# --- ABA 2: MEUS CLIENTES ---
with tabs[1]:
    st.subheader("Minha Carteira")
    op_selecionado = st.selectbox("Quem é você?", ["---"] + st.session_state.operadores)
    
    if op_selecionado != "---":
        meus_dados = df[df['Operador'] == op_selecionado].copy()
        if not meus_dados.empty:
            st.write(f"Clientes atribuídos a {op_selecionado}:")
            # Tabela editável para Status e Data
            colunas = ['Cliente', 'CNJ', 'Status', 'Data_Retorno']
            novo_df = st.data_editor(meus_dados[colunas], use_container_width=True, hide_index=True)
            
            if st.button("💾 Salvar Alterações"):
                st.session_state.clientes.update(novo_df)
                st.success("Dados salvos!")
                st.rerun()
        else:
            st.warning("Você não tem clientes na sua carteira.")

# --- ABA 3: ADMIN ---
with tabs[2]:
    st.subheader("Área do Gestor")
    senha = st.text_input("Senha Admin", type="password")
    
    if senha == "admin123":
        # GERENCIAR OPERADORES
        with st.expander("👥 Equipe"):
            c1, c2 = st.columns(2)
            with c1:
                novo = st.text_input("Novo nome")
                if st.button("Adicionar"):
                    if novo and novo not in st.session_state.operadores:
                        st.session_state.operadores.append(novo)
                        st.rerun()
            with c2:
                remover = st.selectbox("Remover nome", ["---"] + st.session_state.operadores)
                if st.button("Remover"):
                    if remover != "---":
                        st.session_state.operadores.remove(remover)
                        st.rerun()

        # IMPORTAÇÃO E DUPLICIDADE
        with st.expander("📥 Importar Dados"):
            txt = st.text_area("Cole a lista aqui (Nome e CNJ)")
            if st.button("Validar e Importar"):
                linhas = [l.strip() for l in txt.split('\n') if l.strip()]
                for l in linhas:
                    cnj = extrair_cnj(l)
                    nome = l.replace(cnj, "").strip() if cnj != "Sem Processo" else l
                    uid = normalizar_id(nome)
                    
                    # Checagem de duplicidade
                    if uid not in st.session_state.clientes['id'].values:
                        nova_linha = pd.DataFrame([{
                            'id': uid, 'Cliente': nome, 'CNJ': cnj,
                            'Operador': 'Não Atribuído', 'Status': 'Novo',
                            'Data_Retorno': date.today().strftime('%d/%m/%Y')
                        }])
                        st.session_state.clientes = pd.concat([st.session_state.clientes, nova_linha], ignore_index=True)
                st.success("Processamento concluído!")

        # GIRO DE CARTEIRA
        st.subheader("🌀 Giro de Carteira")
        if st.button("EXECUTAR GIRO"):
            if not st.session_state.clientes.empty:
                df_giro = st.session_state.clientes.sample(frac=1).reset_index(drop=True)
                ops = st.session_state.operadores
                for i in range(len(df_giro)):
                    df_giro.at[i, 'Operador'] = ops[i % len(ops)]
                st.session_state.clientes = df_giro
                st.success("Giro realizado!")
                st.rerun()

st.divider()
st.caption(f"Gestão Pro v4.2 | {date.today().strftime('%d/%m/%Y')}")
