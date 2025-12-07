import streamlit as st
import json
import time

# Configuração de CSS Avançada para Layout tipo "Bubble"
st.markdown("""
<style>
    /* 1. Reseta o estilo padrão do container externo da mensagem */
    div[data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0rem !important;
        margin-bottom: 1rem !important;
    }

    /* --- MENSAGEM DO USUÁRIO --- */
    
    /* Inverte a ordem (Avatar na direita) */
    div[data-testid="stChatMessage"]:has(div.user-marker) {
        flex-direction: row-reverse;
    }
    
    /* Estiliza o BALÃO (Conteúdo interno) do usuário */
    div[data-testid="stChatMessage"]:has(div.user-marker) div[data-testid="stChatMessageContent"] {
        background-color: #1B4F72 !important; /* Azul Escuro */
        color: #FFFFFF !important;
        
        /* Formato do balão */
        border-radius: 15px 0px 15px 15px !important; /* Canto pontudo no topo direito */
        padding: 1rem !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        
        /* Posicionamento e Tamanho */
        margin-left: auto !important; /* Empurra para a direita */
        margin-right: 10px !important; /* Espaço entre balão e avatar */
        max-width: 75% !important; /* Limita a largura (efeito GPT/WhatsApp) */
        text-align: right;
    }

    /* Força a cor do texto dentro do balão do usuário */
    div[data-testid="stChatMessage"]:has(div.user-marker) p,
    div[data-testid="stChatMessage"]:has(div.user-marker) div {
        color: #FFFFFF !important;
        text-align: right;
    }
    
    /* --- MENSAGEM DO ASSISTENTE --- */
    
    /* Estiliza o BALÃO do assistente */
    div[data-testid="stChatMessage"]:has(div.assistant-marker) div[data-testid="stChatMessageContent"] {
        background-color: #EBF5FB !important; /* Azul Claro */
        color: #1B4F72 !important;
        border: 1px solid #D6EAF8 !important;
        
        /* Formato do balão */
        border-radius: 0px 15px 15px 15px !important; /* Canto pontudo no topo esquerdo */
        padding: 1rem !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        
        /* Posicionamento e Tamanho */
        margin-right: auto !important; /* Empurra para a esquerda */
        margin-left: 10px !important;
        max-width: 85% !important;
    }
    
    /* Texto do assistente */
    div[data-testid="stChatMessage"]:has(div.assistant-marker) p,
    div[data-testid="stChatMessage"]:has(div.assistant-marker) div {
        color: #1B4F72 !important;
        text-align: left;
    }

    /* Esconde os marcadores técnicos */
    .user-marker, .assistant-marker {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

st.title("💬 Assistente Clínico")

if "qa_chain" not in st.session_state:
    st.error("Você deve selecionar e processar PDFs primeiro!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- FUNÇÃO AUXILIAR PARA EXIBIR MENSAGENS COM MARCADOR E AVATAR ---
def exibir_mensagem(role, content):
    # Define o ícone com base no papel
    icone = "👤" if role == "user" else "🩺"
    
    with st.chat_message(role, avatar=icone):
        # Injeta o marcador invisível para o CSS funcionar
        if role == "user":
            st.markdown('<div class="user-marker"></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="assistant-marker"></div>', unsafe_allow_html=True)
        
        st.markdown(content)

# Exibe histórico
for msg in st.session_state.messages:
    exibir_mensagem(msg["role"], msg["content"])

# Input do usuário
pergunta = st.chat_input("Digite sua pergunta...")

if pergunta:
    # 1. Exibe e salva pergunta do usuário
    st.session_state.messages.append({"role": "user", "content": pergunta})
    exibir_mensagem("user", pergunta)

    # 2. Processa resposta
    with st.chat_message("assistant", avatar="🩺"):
        # Marcador do assistente (para o loading ficar com fundo certo também)
        st.markdown('<div class="assistant-marker"></div>', unsafe_allow_html=True)
        
        placeholder = st.empty()
        placeholder.markdown("⏳ *Pensando...*")
        
        try:
            resposta = st.session_state.qa_chain.invoke({"input": pergunta})
            
            # Tratamento do texto da resposta
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
                        or str(parsed)
                    )
                except Exception:
                    texto = str(resposta)
            
            # Efeito de digitação
            texto_exibido = ""
            for char in texto:
                texto_exibido += char
                placeholder.markdown(texto_exibido + "▌")
                time.sleep(0.002)
            
            placeholder.markdown(texto)
        except Exception as e:
            placeholder.markdown(f"⚠️ Ocorreu um erro ao obter a resposta: {e}")