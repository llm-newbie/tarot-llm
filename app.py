# Streamlit app for TarotLLM

import sys
import os

# Force UTF-8 encoding on Windows
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"

import streamlit as st
from src.tarot_reader import TarotReader

# Streamlit page config
st.set_page_config(
    page_title="TarotLLM",
    page_icon="🌙",
    layout="centered",
    initial_sidebar_state="expanded",
)

# UI and CSS
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;500&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"], [data-testid="stAppViewContainer"] {
    background-color: #EDE8F5 !important;
    font-family: 'Inter', sans-serif !important;
    color: #2D2A4A !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: #E2DCF0 !important;
    border-right: 1px solid #C5B8E8 !important;
}
section[data-testid="stSidebar"] * {
    color: #2D2A4A !important;
}

/* ── Main container ── */
[data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
}

/* ── Header bar ── */
.tarot-header {
    background-color: #1E1B3A;
    color: #FFFFFF;
    padding: 18px 28px;
    border-radius: 0 0 16px 16px;
    margin-bottom: 24px;
    text-align: center;
    font-family: 'Playfair Display', serif;
}
.tarot-header h1 {
    margin: 0;
    font-size: 1.7rem;
    font-weight: 700;
    color: #FFFFFF !important;
    letter-spacing: 0.08em;
}
.tarot-header p {
    margin: 4px 0 0;
    font-size: 0.82rem;
    color: #C5B8E8 !important;
    font-style: italic;
    letter-spacing: 0.04em;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 4px 0 !important;
}

/* User message */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: #FFFFFF !important;
    border: 1px solid #C5B8E8 !important;
    border-radius: 14px !important;
    padding: 12px 16px !important;
    margin-bottom: 8px !important;
}

/* Assistant message */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: #FFFFFF !important;
    border: 1px solid #6B5FA633 !important;
    border-left: 4px solid #6B5FA6 !important;
    border-radius: 14px !important;
    padding: 12px 16px !important;
    margin-bottom: 8px !important;
}

/* Message text */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span {
    color: #2D2A4A !important;
    font-size: 0.97rem !important;
    line-height: 1.7 !important;
}

/* ── Card row ── */
.card-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 10px 0 14px;
}
.card-chip {
    background: #EDE8F5;
    border: 1px solid #6B5FA655;
    border-radius: 8px;
    padding: 5px 12px;
    font-size: 0.78rem;
    color: #6B5FA6;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
}
.card-chip .orient {
    color: #C5B8E8;
    font-size: 0.7rem;
    margin-left: 4px;
}

/* ── Spread badge ── */
.spread-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #1E1B3A;
    color: #C5B8E8;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.72rem;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    letter-spacing: 0.04em;
    margin-bottom: 10px;
}

/* ── Welcome card ── */
.welcome-card {
    background: #FFFFFF;
    border: 1px solid #C5B8E8;
    border-top: 4px solid #6B5FA6;
    border-radius: 14px;
    padding: 22px 26px;
    margin-bottom: 20px;
}
.welcome-card h3 {
    color: #1E1B3A !important;
    font-family: 'Playfair Display', serif !important;
    font-size: 1.1rem !important;
    margin-bottom: 10px !important;
}
.welcome-card p {
    color: #7B7498 !important;
    font-size: 0.88rem !important;
    line-height: 1.65 !important;
    margin: 0 !important;
}
.example-chip {
    display: inline-block;
    background: #EDE8F5;
    border: 1px solid #C5B8E8;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.8rem;
    color: #6B5FA6;
    margin: 4px 3px 0;
    cursor: default;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: #FFFFFF !important;
    border: 1px solid #C5B8E8 !important;
    border-radius: 14px !important;
    min-height: 52px !important;
    max-height: 52px !important;
    overflow: hidden !important;
}
[data-testid="stChatInput"] textarea {
    background: #FFFFFF !important;
    color: #2D2A4A !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    border: none !important;
    max-height: 32px !important;
    min-height: 32px !important;
    overflow-y: auto !important;
    resize: none !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #B0A8CC !important;
}

/* ── Sidebar label ── */
.sidebar-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: #7B7498;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 16px 0 4px;
}

/* ── API key input ── */
[data-testid="stTextInput"] input {
    background: #FFFFFF !important;
    border: 1px solid #C5B8E8 !important;
    color: #2D2A4A !important;
    border-radius: 8px !important;
}

/* ── Reset button ── */
.stButton > button {
    background: #FFFFFF !important;
    color: #6B5FA6 !important;
    border: 1px solid #C5B8E8 !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    width: 100% !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    background: #EDE8F5 !important;
    border-color: #6B5FA6 !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] { color: #6B5FA6 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #EDE8F5; }
::-webkit-scrollbar-thumb { background: #C5B8E8; border-radius: 4px; }

/* ── Hide streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Avatar icons ── */
[data-testid="chatAvatarIcon-user"] { background: #C5B8E8 !important; }
[data-testid="chatAvatarIcon-assistant"] { background: #1E1B3A !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# Determine if the message is a follow-up question
def _is_followup(prompt: str, messages: list) -> bool:
    if len(messages) < 2:
        return False
    signals = ["그럼", "그러면", "더 자세히", "왜", "구체적으로", "이 카드", "그 카드",
               "조금 더", "어떻게", "무슨 의미", "tell me more", "why", "explain"]
    return len(prompt) < 45 or any(s in prompt for s in signals)

# Render card info as HTML chips
def _card_chips_html(positions: list, cards: list) -> str:
    chips = []
    for pos, card in zip(positions, cards):
        orient = "↑" if card["orientation"] == "upright" else "↓"
        chips.append(
            f'<span class="card-chip">'
            f'{card["name"]}<span class="orient">{orient}</span>'
            f'</span>'
        )
    return f'<div class="card-row">{"".join(chips)}</div>'


# Initialize session state
for key, val in {
    "messages": [],
    "reader": None,
    "api_ok": False,
    "_last_key": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = val


# Sidebar
with st.sidebar:
    st.markdown(
        '<div style="text-align:center; padding: 12px 0 4px;">'
        '<span style="font-size:2rem;">🌙</span><br>'
        '<span style="font-family:\'Playfair Display\',serif; font-size:1.2rem; '
        'font-weight:700; color:#1E1B3A;">TarotLLM</span><br>'
        '<span style="font-size:0.73rem; color:#7B7498; font-style:italic;">AI Tarot Reading</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown('<div class="sidebar-label">Gemini API Key</div>', unsafe_allow_html=True)
    api_key_input = st.text_input(
        "API Key",
        type="password",
        value=os.environ.get("GEMINI_API_KEY", ""),
        placeholder="AIza...",
        label_visibility="collapsed",
    )
    if api_key_input and api_key_input != st.session_state._last_key:
        try:
            st.session_state.reader = TarotReader(api_key=api_key_input)
            st.session_state.api_ok = True
            st.session_state._last_key = api_key_input
        except Exception as e:
            st.error(str(e))

    if st.session_state.api_ok:
        st.markdown(
            '<div style="font-size:0.75rem; color:#6B5FA6; margin-top:4px;">● 연결됨</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    if st.button("대화 초기화"):
        st.session_state.messages = []
        if st.session_state.reader:
            st.session_state.reader._history = []
            st.session_state.reader._last_context = ""
        st.rerun()

    st.markdown(
        '<div style="font-size:0.68rem; color:#B0A8CC; text-align:center; margin-top:20px;">'
        'Powered by Gemini 2.5 Flash</div>',
        unsafe_allow_html=True,
    )


# Header
st.markdown(
    '<div class="tarot-header">'
    '<h1>✦ TarotLLM ✦</h1>'
    '<p>AI가 카드를 뽑고, 당신의 이야기를 읽어드립니다</p>'
    '</div>',
    unsafe_allow_html=True,
)

# Welcome screen
if not st.session_state.messages:
    st.markdown(
        '<div class="welcome-card">'
        '<h3>어떤 고민이 있으신가요?</h3>'
        '<p>고민이나 질문을 자유롭게 입력하세요. '
        '엔진이 질문을 분석하여 가장 적합한 배열을 선택하고, '
        '카드를 뽑아 해석을 스트리밍으로 전달합니다.</p>'
        '<div style="margin-top:14px;">'
        '<span class="example-chip">나의 연애운은?</span>'
        '<span class="example-chip">직장을 바꿔야 할까요?</span>'
        '<span class="example-chip">오늘의 카드 뽑기</span>'
        '<span class="example-chip">재정 상황이 걱정돼요</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

# Render chat history
for msg in st.session_state.messages:
    avatar = "🧑" if msg["role"] == "user" else "🌙"
    with st.chat_message(msg["role"], avatar=avatar):
        if msg["role"] == "assistant" and msg.get("meta"):
            m = msg["meta"]
            st.markdown(
                f'<div class="spread-badge">🂠 {m["spread_name"]} &nbsp;·&nbsp; {m["num_cards"]}장</div>',
                unsafe_allow_html=True,
            )
            st.markdown(_card_chips_html(m["positions"], m["cards"]), unsafe_allow_html=True)
        st.markdown(msg["content"])


# Chat input
if prompt := st.chat_input("질문을 입력하세요..."):
    if not st.session_state.api_ok:
        st.warning("사이드바에서 Gemini API 키를 먼저 입력해주세요.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🌙"):
        followup_mode = _is_followup(prompt, st.session_state.messages)

        if followup_mode:
            response_text = ""
            placeholder = st.empty()
            try:
                for chunk in st.session_state.reader.stream_followup(prompt):
                    response_text += chunk
                    placeholder.markdown(response_text + "▌")
                placeholder.markdown(response_text)
            except Exception as e:
                st.error(f"오류: {e}")
                st.stop()

            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "meta": None,
            })

        else:
            meta = None
            response_text = ""
            meta_placeholder = st.empty()
            text_placeholder = st.empty()

            try:
                stream = st.session_state.reader.stream_reading(prompt)

                for kind, payload in stream:
                    if kind == "meta":
                        meta = payload
                        badge = (
                            f'<div class="spread-badge">'
                            f'🂠 {meta["spread_name"]} &nbsp;·&nbsp; {meta["num_cards"]}장'
                            f'</div>'
                        )
                        chips = _card_chips_html(meta["positions"], meta["cards"])
                        meta_placeholder.markdown(badge + chips, unsafe_allow_html=True)

                    elif kind == "chunk":
                        response_text += payload
                        text_placeholder.markdown(response_text + "▌")

                text_placeholder.markdown(response_text)

            except Exception as e:
                st.error(f"오류: {e}")
                st.stop()

            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "meta": meta,
            })
