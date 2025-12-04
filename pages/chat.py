import streamlit as st
import json
import time

# CSS para diferenciar visualmente user e assistant
st.markdown("""
<style>
    /* Container geral das mensagens */
    div.stChatMessage[data-testid="stChatMessage"] {
        padding: 14px !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
    }
    
    /* Mensagens do usuário - azul escuro */
    div.stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        background-color: #2874A6 !important;
        border: 1px solid #1F618D !important;
    }
    
    div.stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) p,
    div.stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div {
        color: #FFFFFF !important;
    }
    
    /* Mensagens do assistente - azul claro */
    div.stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
        background-color: #D6EAF8 !important;
        border: 1px solid #AED6F1 !important;
    }
    
    div.stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) p,
    div.stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) div {
        color: #1B4F72 !important;
    }
    
    /* Animação de carregamento */
    .loading-dots {
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    
    .loading-dots span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #5DADE2;
        animation: bounce 1.4s infinite ease-in-out both;
    }
    
    .loading-dots span:nth-child(1) {
        animation-delay: -0.32s;
    }
    
    .loading-dots span:nth-child(2) {
        animation-delay: -0.16s;
    }
    
    @keyframes bounce {
        0%, 80%, 100% { 
            transform: scale(0);
            opacity: 0.5;
        }
        40% { 
            transform: scale(1);
            opacity: 1;
        }
    }
</style>
""", unsafe_allow_html=True)

st.title("💬 Assistente Clínico")

if "qa_chain" not in st.session_state:
    st.error("Você deve selecionar e processar PDFs primeiro!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe histórico de mensagens
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Campo de entrada
pergunta = st.chat_input("Digite sua pergunta...")

if pergunta:
    # Adiciona mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    # Mostra animação de carregamento
    with st.chat_message("assistant"):
        loading_placeholder = st.empty()
        loading_placeholder.markdown("""
        <div class="loading-dots">
            <span></span>
            <span></span>
            <span></span>
        </div>
        <p style="display: inline; margin-left: 12px; color: #5DADE2;">Pensando...</p>
        """, unsafe_allow_html=True)
        
        # Processa a resposta da IA
        try:
            resposta = st.session_state.qa_chain.invoke({"input": pergunta})
            
            # Extrai o texto da resposta
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
            
            # Remove o loading
            loading_placeholder.empty()
            
            # Animação de digitação
            texto_placeholder = st.empty()
            exibido = ""
            
            for char in texto:
                exibido += char
                texto_placeholder.markdown(exibido)
                time.sleep(0.004)
            
            # Salva no histórico
            st.session_state.messages.append({"role": "assistant", "content": texto})
            
        except Exception as e:
            loading_placeholder.empty()
            st.error(f"Erro ao processar resposta: {str(e)}")