import streamlit as st
import pandas as pd
from datetime import datetime, date
import re

# 1. CONFIGURAÇÃO E ESTILO (CSS)
st.set_page_config(page_title="Gestão Pro v4.2", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
    .main-title {text-align: center; color: #1E3A8A; font-weight: bold; margin-bottom: 20px;}
    .stTabs [data-baseweb="tab-list"] {gap: 10px; justify-content: center;}
    .stTabs [data-baseweb="tab"] {background-color: #f1f5f9; border-radius: 5px; padding: 10px 20px;}
    .stTabs [aria-selected="true"] {background-color: #1E3A8A !important; color: white !important;}
</style>
""", unsafe_content_html=True)

# 2. INICIALIZAÇÃO DO BANCO (SESSION STATE)
if 'clientes' not in st.session_state:
    st.session_state.clientes = pd.DataFrame(columns=['id', 'Cliente', 'CNJ', 'Operador', 'Status', 'Ultimo_Contato', 'Data_Retorno'])

if 'operadores' not in st.session_state:
    st.session_state.operadores = ["Diego", "Samara", "Natan"]

# 3. FUNÇÕES DE SUPORTE
def normalizar_nome(texto):
    return re.sub(r'[^a-zA-Z0-9]', '', str(texto)).upper()

def aplicar_mascara_cnj(texto):
    padrao = r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}'
    resultado = re.findall(padrao, texto)
    return resultado[0] if resultado else "Sem Processo"

def colorir_tabela(val):
    try:
        data_ret = datetime.strptime(val, '%d/%m/%Y').date()
        hoje = date.today()
        if data_ret < hoje: return 'background-color: #fee2e2; color: #991b1b' # Atrasado
        if data_ret == hoje: return 'background-color: #fef9c3; color: #854d0e' # Hoje
        return 'background-color: #dcfce7; color: #166534' # Agendado
    except: return ''

# 4. INTERFACE PRINCIPAL
st.markdown("<h1 class='main-title'>🚀 Gestão Pro v4.2</h1>", unsafe_content_html=True)
tabs = st.tabs(["📊 DASHBOARD", "👤 MEUS CLIENTES", "🛠️ ADMINISTRAÇÃO"])

# --- ABA 1: DASHBOARD (SOMENTE INFORMAÇÕES) ---
with tabs[0]:
    st.subheader("Resumo da Carteira")
    df = st.session_state.clientes
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Total Clientes", len(df))
    col2.metric("Atribuídos", len(df[df['Operador'] != 'Não Atribuído']))
    
    if not df.empty:
        # Converter string para data para contagem
        df['dt_temp'] = pd.to_datetime(df['Data_Retorno'], format='%d/%m/%Y').dt.date
        atrasados = len(df[df['dt_temp'] < date.today()])
        hoje = len(df[df['dt_temp'] == date.today()])
        col3.metric("🚨 Atrasados", atrasados)
        col4.metric("📅 Para Hoje", hoje)
    
    st.divider()
    st.info("Utilize as abas superiores para gerenciar os dados.")

# --- ABA 2: MEUS CLIENTES (SELEÇÃO POR OPERADOR) ---
with tabs[1]:
    st.subheader("Filtro por Operador")
    op_selecionado = st.selectbox("Selecione seu nome:", ["---"] + st.session_state.operadores)
    
    if op_selecionado != "---":
        meus_clientes = df[df['Operador'] == op_selecionado].copy()
        if not meus_clientes.empty:
            st.write(f"Clientes de **{op_selecionado}**:")
            # Editor de tabela para status e data
            colunas_visiveis = ['Cliente', 'CNJ', 'Status', 'Data_Retorno']
            editado = st.data_editor(meus_clientes[colunas_visiveis], use_container_width=True, hide_index=True)
            
            if st.button("Salvar Alterações"):
                for index, row in editado.iterrows():
                    # Localiza no banco original pelo índice e atualiza
                    idx_original = meus_clientes.index[index]
                    st.session_state.clientes.loc[idx_original, ['Status', 'Data_Retorno']] = [row['Status'], row['Data_Retorno']]
                st.success("Dados atualizados!")
                st.rerun()
        else:
            st.warning("Nenhum cliente atribuído a você.")

# --- ABA 3: ADMINISTRAÇÃO ---
with tabs[2]:
    senha = st.text_input("Senha de Acesso", type="password")
    if senha == "admin123":
        
        # GERENCIAR OPERADORES
        with st.expander("👥 Gerenciar Equipe (Adicionar/Excluir)"):
            col_add, col_del = st.columns(2)
            with col_add:
                novo_op = st.text_input("Nome do Operador")
                if st.button("Adicionar à Equipe"):
                    if novo_op and novo_op not in st.session_state.operadores:
                        st.session_state.operadores.append(novo_op)
                        st.rerun()
            with col_del:
                op_para_remover = st.selectbox("Excluir Operador:", ["---"] + st.session_state.operadores)
                if st.button("❌ Remover"):
                    if op_para_remover != "---":
                        st.session_state.operadores.remove(op_para_remover)
                        st.rerun()

        # IMPORTAÇÃO COM DUPLICIDADE
        with st.expander("📥 Importar Clientes (Evita Duplicados)"):
            texto = st.text_area("Cole os nomes/processos (um por linha)")
            if st.button("Processar Importação"):
                linhas = [l.strip() for l in texto.split('\n') if l.strip()]
                novos_cont = 0
                duplicados_cont = 0
                
                for l in linhas:
                    cnj = aplicar_mascara_cnj(l)
                    nome_limpo = l.replace(cnj, "").strip() if cnj != "Sem Processo" else l
                    id_unico = normalizar_nome(nome_limpo)
                    
                    # Checar duplicidade no banco
                    if id_unico not in st.session_state.clientes['id'].values:
                        novo_dado = pd.DataFrame([{
                            'id': id_unico,
                            'Cliente': nome_limpo,
                            'CNJ': cnj,
                            'Operador': 'Não Atribuído',
                            'Status': 'Novo',
                            'Ultimo_Contato': date.today().strftime('%d/%m/%Y'),
                            'Data_Retorno': date.today().strftime('%d/%m/%Y')
                        }])
                        st.session_state.clientes = pd.concat([st.session_state.clientes, novo_dado], ignore_index=True)
                        novos_cont += 1
                    else:
                        duplicados_cont += 1
                
                st.success(f"Sucesso: {novos_cont} novos. Duplicados ignorados: {duplicados_cont}")

        # GIRO DE CARTEIRA
        st.subheader("🌀 Giro de Carteira")
        if st.button("EXECUTAR GIRO EQUITATIVO"):
            if not st.session_state.clientes.empty and st.session_state.operadores:
                df_temp = st.session_state.clientes.sample(frac=1).reset_index(drop=True)
                ops = st.session_state.operadores
                for i in range(len(df_temp)):
                    df_temp.at[i, 'Operador'] = ops[i % len(ops)]
                st.session_state.clientes = df_temp
                st.success("Clientes redistribuídos entre todos os operadores!")
                st.rerun()

        if st.button("Limpar Tudo (Reset)"):
            st.session_state.clientes = pd.DataFrame(columns=['id', 'Cliente', 'CNJ', 'Operador', 'Status', 'Ultimo_Contato', 'Data_Retorno'])
            st.rerun()

# RODAPÉ
st.divider()
st.caption(f"Gestão Pro v4.2 | {date.today().strftime('%d/%m/%Y')}")
