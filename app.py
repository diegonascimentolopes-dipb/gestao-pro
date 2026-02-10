import streamlit as st
import pandas as pd
from datetime import datetime, date
import re

# 1. CONFIGURAÇÃO (O Tema escuro/claro é controlado pelo navegador/usuário no menu superior direito)
st.set_page_config(page_title="Gestão Pro v4.2", layout="wide", initial_sidebar_state="collapsed")

# 2. INICIALIZAÇÃO
if 'clientes' not in st.session_state:
    st.session_state.clientes = pd.DataFrame(columns=['Cliente', 'CNJ', 'Operador', 'Status', 'Data_Retorno'])

if 'operadores' not in st.session_state:
    st.session_state.operadores = ["Diego", "Samara", "Natan"]

# 3. FUNÇÕES LÓGICAS
def limpar_texto(t):
    return re.sub(r'[^A-Z0-9]', '', str(t).upper())

def extrair_cnj(texto):
    # Regex rigoroso para o padrão CNJ
    padrao = r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}'
    resultado = re.findall(padrao, texto)
    return resultado[0] if resultado else "Sem Processo"

# 4. INTERFACE
st.title("🚀 Gestão Pro v4.2")

tabs = st.tabs(["📊 DASHBOARD", "👤 MEUS CLIENTES", "🛠️ ADMIN"])

# --- ABA 1: DASHBOARD ---
with tabs[0]:
    df = st.session_state.clientes
    m1, m2, m3 = st.columns(3)
    m1.metric("Total de Clientes", len(df))
    m2.metric("Equipe Ativa", len(st.session_state.operadores))
    
    if not df.empty:
        # Lógica de prazos
        df['dt_temp'] = pd.to_datetime(df['Data_Retorno'], errors='coerce').dt.date
        atrasados = len(df[df['dt_temp'] < date.today()])
        m3.metric("🚨 Prazos Vencidos", atrasados)
    
    st.divider()
    st.info("As alterações feitas na aba 'Meus Clientes' são salvas automaticamente.")

# --- ABA 2: MEUS CLIENTES (SALVAMENTO AUTOMÁTICO) ---
with tabs[1]:
    op_selecionado = st.selectbox("Selecione seu nome:", ["---"] + st.session_state.operadores)
    
    if op_selecionado != "---":
        # Filtramos os clientes do operador
        mask = st.session_state.clientes['Operador'] == op_selecionado
        meus_clientes = st.session_state.clientes[mask]
        
        if not meus_clientes.empty:
            # st.data_editor com salvamento automático via session_state
            edited_df = st.data_editor(
                meus_clientes,
                column_config={
                    "Data_Retorno": st.column_config.DateColumn(
                        "Data de Retorno",
                        format="DD/MM/YYYY",
                        min_value=date(2025, 1, 1),
                    ),
                    "CNJ": st.column_config.TextColumn("Processo CNJ", max_chars=25),
                    "Status": st.column_config.SelectboxColumn("Status", options=["Novo", "Em Análise", "Acionado", "Finalizado"])
                },
                use_container_width=True,
                hide_index=True,
                key="editor_carteira"
            )
            
            # Lógica para persistir as mudanças de volta ao dataframe principal
            if st.session_state.get("editor_carteira"):
                for idx, changes in st.session_state.editor_carteira['edited_rows'].items():
                    real_idx = meus_clientes.index[idx]
                    for col, val in changes.items():
                        st.session_state.clientes.loc[real_idx, col] = val
        else:
            st.warning("Nenhum cliente na sua carteira.")

# --- ABA 3: ADMIN ---
with tabs[2]:
    senha = st.text_input("Senha Admin", type="password")
    if senha == "admin123":
        # GERENCIAR EQUIPE
        with st.expander("👥 Equipe"):
            c1, c2 = st.columns(2)
            with c1:
                novo = st.text_input("Novo Operador")
                if st.button("Adicionar"):
                    if novo and novo not in st.session_state.operadores:
                        st.session_state.operadores.append(novo)
                        st.rerun()
            with c2:
                remover = st.selectbox("Remover Operador", ["---"] + st.session_state.operadores)
                if st.button("Excluir"):
                    if remover != "---":
                        st.session_state.operadores.remove(remover)
                        st.rerun()

        # IMPORTAÇÃO COM VALIDAÇÃO ANTI-REPETIÇÃO
        with st.expander("📥 Importar e Higienizar"):
            txt = st.text_area("Cole a lista aqui")
            if st.button("Importar"):
                linhas = [l.strip() for l in txt.split('\n') if l.strip()]
                banco = st.session_state.clientes
                
                for l in linhas:
                    cnj = extrair_cnj(l)
                    nome = l.replace(cnj, "").strip() if cnj != "Sem Processo" else l
                    
                    # Validação: Checa se o CNJ já existe ou se o Nome Limpo já existe
                    existe_cnj = (cnj != "Sem Processo") and (cnj in banco['CNJ'].values)
                    existe_nome = limpar_texto(nome) in banco['Cliente'].apply(limpar_texto).values
                    
                    if not existe_cnj and not existe_nome:
                        nova_linha = pd.DataFrame([{
                            'Cliente': nome, 'CNJ': cnj,
                            'Operador': 'Não Atribuído', 'Status': 'Novo',
                            'Data_Retorno': date.today()
                        }])
                        st.session_state.clientes = pd.concat([st.session_state.clientes, nova_linha], ignore_index=True)
                st.success("Importação concluída. Duplicados foram ignorados.")

        # GIRO
        if st.button("🌀 EXECUTAR GIRO EQUITATIVO"):
            if not st.session_state.clientes.empty:
                df_giro = st.session_state.clientes.sample(frac=1).reset_index(drop=True)
                ops = st.session_state.operadores
                for i in range(len(df_giro)):
                    df_giro.at[i, 'Operador'] = ops[i % len(ops)]
                st.session_state.clientes = df_giro
                st.rerun()

st.divider()
st.caption(f"Gestão Pro v4.2 | {date.today().strftime('%d/%m/%Y')}")
