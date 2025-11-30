import streamlit as st
import os

st.set_page_config(page_title="LLM Saúde", page_icon="🩺")

USERNAME = "admin"
PASSWORD = "admin"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login_screen():
    st.title("🔐 Login - LLM Saúde")
    user = st.text_input("Usuário")
    pwd = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user == USERNAME and pwd == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Credenciais inválidas!")

if not st.session_state.logged_in:
    login_screen()
    st.stop()

# Já autenticado → redireciona para a página de PDFs
st.switch_page("pages/pdf_selector.py")
