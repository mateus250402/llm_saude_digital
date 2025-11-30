import streamlit as st
import json
from collections import defaultdict

st.title("💬 Assistente Clínico")

if "qa_chain" not in st.session_state:
    st.error("Você deve selecionar e processar PDFs primeiro!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

pergunta = st.chat_input("Digite sua pergunta...")

if pergunta:
    # registra a pergunta no histórico e exibe imediatamente
    st.session_state.messages.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.write(pergunta)

    # chama a chain e extrai texto (suporta dicts com chaves em pt/eng)
    resposta = st.session_state.qa_chain.invoke({"input": pergunta})

    if isinstance(resposta, dict):
        texto = (
            resposta.get("resposta")
            or resposta.get("answer")
            or resposta.get("result")
            or resposta.get("output")
            or resposta.get("text")
            or str(resposta)
        )
    else:
        # resposta pode ser string (texto ou JSON serializado) — tenta parsear JSON, senão usa string
        try:
            parsed = json.loads(resposta)
            texto = (
                parsed.get("resposta")
                or parsed.get("answer")
                or parsed.get("result")
                or parsed.get("output")
                or parsed.get("text")
                or str(parsed)
            )
        except Exception:
            texto = str(resposta)

    st.session_state.messages.append({"role": "assistant", "content": texto})

    with st.chat_message("assistant"):
        st.write(texto)