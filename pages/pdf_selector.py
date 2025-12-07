import streamlit as st
import os
from pipeline import run_pipeline

st.title("📂 Seleção de Protocolos em PDF")

# Verifica login
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Faça login primeiro.")
    st.stop()

# Pasta dos PDFs
PDF_DIR = "pdf"
os.makedirs(PDF_DIR, exist_ok=True)

# Lista arquivos PDF
pdfs = [f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")]

if not pdfs:
    st.warning("Nenhum PDF encontrado na pasta 'pdf/'. Adicione arquivos e recarregue.")
    st.stop()

# Checkbox para selecionar todos
selecionar_todos = st.checkbox("Selecionar todos os protocolos")

if selecionar_todos:
    opcoes = st.multiselect("Selecione os protocolos que deseja utilizar:", pdfs, default=pdfs)
else:
    opcoes = st.multiselect("Selecione os protocolos que deseja utilizar:", pdfs)

if st.button("Processar PDFs") and opcoes:

    caminhos = [os.path.join(PDF_DIR, p) for p in opcoes]

    # TELA DE LOADING
    with st.spinner("⏳ Processando documentos, extraindo textos, criando embeddings e preparando a IA..."):
        st.session_state.qa_chain, \
        st.session_state.stuff_chain, \
        st.session_state.all_docs = run_pipeline(caminhos)

    st.toast("✅ Protocolos processados com sucesso!")
    st.success("Redirecionando para o chat...")

    st.switch_page("pages/chat.py")