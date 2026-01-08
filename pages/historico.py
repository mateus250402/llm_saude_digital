import streamlit as st
import json
from pathlib import Path
from datetime import datetime


# ====== CONFIG ======
st.set_page_config(page_title="Histórico", page_icon="🕘", layout="wide")

BASE_DIR = Path(__file__).resolve().parent.parent
HISTORY_FILE = BASE_DIR / "output" / "history.json"


# ====== VERIFICA LOGIN ======
def verificar_login():
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.error("🔒 Faça login para acessar o histórico.")
        st.stop()


# ====== CSS ======
def carregar_css():
    st.markdown("""
    <style>
        div[data-testid="stChatMessage"] {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0rem !important;
            margin-bottom: 1rem !important;
        }

        div[data-testid="stChatMessage"]:has(div.user-marker) {
            flex-direction: row-reverse;
        }

        div[data-testid="stChatMessage"]:has(div.user-marker) div[data-testid="stChatMessageContent"] {
            background-color: #1B4F72 !important;
            color: #FFFFFF !important;
            border-radius: 15px 0px 15px 15px !important;
            padding: 1rem !important;
            margin-left: auto !important;
            margin-right: 10px !important;
            max-width: 70% !important;
            text-align: right;
        }

        div[data-testid="stChatMessage"]:has(div.user-marker) p,
        div[data-testid="stChatMessage"]:has(div.user-marker) div {
            color: #FFFFFF !important;
            text-align: right;
        }

        div[data-testid="stChatMessage"]:has(div.assistant-marker) div[data-testid="stChatMessageContent"] {
            background-color: #EBF5FB !important;
            color: #1B4F72 !important;
            border: 1px solid #D6EAF8 !important;
            border-radius: 0px 15px 15px 15px !important;
            padding: 1rem !important;
            margin-right: auto !important;
            margin-left: 10px !important;
            max-width: 80% !important;
        }

        div[data-testid="stChatMessage"]:has(div.assistant-marker) p,
        div[data-testid="stChatMessage"]:has(div.assistant-marker) div {
            color: #1B4F72 !important;
            text-align: left;
        }

        .user-marker, .assistant-marker {
            display: none;
        }

        .data-hora {
            font-size: 0.75rem;
            color: #888;
            margin-top: 4px;
        }
    </style>
    """, unsafe_allow_html=True)


# ====== UTIL ======
def formatar_data_hora(raw: str) -> str:
    try:
        dt = datetime.strptime(raw, "%Y%m%d_%H%M%S")
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return raw


def exibir_mensagem(role, content, data_hora=None):
    icone = "👤" if role == "user" else "🤖"

    with st.chat_message(role, avatar=icone):
        if role == "user":
            st.markdown('<div class="user-marker"></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="assistant-marker"></div>', unsafe_allow_html=True)

        st.markdown(content)

        if data_hora:
            st.markdown(f"<div class='data-hora'>{data_hora}</div>", unsafe_allow_html=True)


# ====== HISTÓRICO ======
def carregar_historico():
    if not HISTORY_FILE.exists():
        st.info("Nenhum histórico encontrado ainda.")
        st.stop()

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    except json.JSONDecodeError:
        st.error("Erro ao ler o arquivo de histórico.")
        st.stop()

    if not history:
        st.info("Histórico vazio.")
        st.stop()

    for item in history:
        raw = item.get("data_hora", "")
        item["data_formatada"] = formatar_data_hora(raw)

    return history


def aplicar_filtros(history):
    st.markdown("### 🎛️ Filtros")

    col1, col2, col3, col4 = st.columns([2, 2, 3, 2])

    with col1:
        modo = st.selectbox(
            "Modo de visualização",
            ["Nenhum (não mostrar nada)", "Ver tudo", "Filtrar por dia"]
        )

    with col2:
        datas_disponiveis = sorted(
            list(set([item["data_hora"][:8] for item in history]))
        )

        data_selecionada = None
        if modo == "Filtrar por dia":
            data_selecionada = st.selectbox(
                "📅 Dia",
                datas_disponiveis,
                format_func=lambda d: datetime.strptime(d, "%Y%m%d").strftime("%d/%m/%Y")
            )
        else:
            st.selectbox("📅 Dia", ["—"], disabled=True)

    with col3:
        termo = st.text_input("🔍 Buscar por texto")

    with col4:
        ordem_recente = st.checkbox("Mais recentes primeiro", value=True)

    filtrado = history

    if modo == "Nenhum (não mostrar nada)":
        filtrado = []

    if modo == "Filtrar por dia" and data_selecionada:
        filtrado = [
            item for item in filtrado
            if item["data_hora"].startswith(data_selecionada)
        ]

    if termo:
        termo_lower = termo.lower()
        filtrado = [
            item for item in filtrado
            if termo_lower in item.get("pergunta", "").lower()
            or termo_lower in item.get("resposta", "").lower()
        ]

    if ordem_recente:
        filtrado = sorted(filtrado, key=lambda x: x["data_hora"], reverse=True)
    else:
        filtrado = sorted(filtrado, key=lambda x: x["data_hora"])

    return filtrado


# ====== MAIN ======
def main():
    verificar_login()
    carregar_css()

    st.title("🕘 Histórico de Perguntas e Respostas")

    history = carregar_historico()
    filtrado = aplicar_filtros(history)

    if not filtrado:
        st.info("Nenhum registro para exibir com os filtros atuais.")
        return

    for item in filtrado:
        pergunta = item.get("pergunta", "")
        resposta = item.get("resposta", "")
        data_fmt = item.get("data_formatada", "")

        exibir_mensagem("user", pergunta, data_fmt)
        exibir_mensagem("assistant", resposta)


# ====== RUN ======
if __name__ == "__main__":
    main()
