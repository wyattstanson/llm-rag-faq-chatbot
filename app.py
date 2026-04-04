import streamlit as st
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from config.settings import FINANCE_SYSTEM_PROMPT, GENERAL_SYSTEM_PROMPT
from memory.chat_memory import (
    create_conversation, get_conversations, get_conversation,
    add_message, get_messages, get_recent_messages_for_llm,
    update_conversation_title, delete_conversation, toggle_pin
)
from llm.client import stream_response
from llm.prompt_builder import build_messages
from rag.retriever import retrieve, format_context
from rag.ingestion import ingest_bytes, ingest_directory
from rag.vector_store import list_sources, get_doc_count
from rai.policy_engine import is_safe, get_refusal_message
from rai.evaluator import evaluate_response
from news.fetcher import (
    fetch_news, fetch_market_data, fetch_sector_performance,
    fetch_fear_greed, fetch_sparkline_data
)

st.set_page_config(
    page_title="Aria",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="expanded"
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --black:   #0a0a0a;
    --bg:      #111111;
    --surface: #161616;
    --surface2:#1e1e1e;
    --border:  #222222;
    --border2: #2e2e2e;
    --text:    #e8e8e8;
    --muted:   #888888;
    --dim:     #444444;
    --accent:  #e50914;
    --blue:    #3b82f6;
    --green:   #22c55e;
    --red:     #ef4444;
    --amber:   #f59e0b;
    --radius:  4px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, sans-serif !important;
    background: var(--black) !important;
    color: var(--text) !important;
    font-size: 14px;
    -webkit-font-smoothing: antialiased;
}

.main .block-container { padding: 0 !important; max-width: 100% !important; }
header[data-testid="stHeader"] { display: none !important; }
.stDeployButton { display: none !important; }
#MainMenu { display: none !important; }
footer { display: none !important; }
.stApp { background: var(--black) !important; }

section[data-testid="stSidebar"] {
    background: var(--bg) !important;
    border-right: 1px solid var(--border) !important;
    width: 240px !important;
}
section[data-testid="stSidebar"] > div {
    background: var(--bg) !important;
    padding: 0 !important;
}

.s-wordmark { padding: 28px 20px 20px; border-bottom: 1px solid var(--border); margin-bottom: 4px; }
.s-wordmark-name { font-size: 17px; font-weight: 600; letter-spacing: -0.3px; color: var(--text); }
.s-wordmark-sub { font-size: 10px; color: var(--dim); letter-spacing: 1.8px; text-transform: uppercase; margin-top: 3px; }
.s-section-label { font-size: 9px; font-weight: 600; letter-spacing: 1.8px; text-transform: uppercase; color: var(--dim); padding: 16px 20px 6px; }
.doc-pill { display: inline-flex; align-items: center; padding: 3px 8px; background: var(--surface2); border: 1px solid var(--border); border-radius: 2px; font-size: 10px; color: var(--muted); margin: 2px; font-family: 'JetBrains Mono', monospace; }

.stButton > button {
    background: transparent !important;
    color: var(--muted) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 12.5px !important;
    font-weight: 400 !important;
    padding: 8px 14px !important;
    transition: all 0.12s !important;
    width: 100% !important;
    text-align: left !important;
}
.stButton > button:hover {
    background: var(--surface) !important;
    color: var(--text) !important;
    border-color: var(--border2) !important;
}

.topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 36px; height: 56px;
    border-bottom: 1px solid var(--border);
    background: var(--bg);
    position: sticky; top: 0; z-index: 100;
}
.topbar-left { display: flex; align-items: center; gap: 12px; }
.topbar-title { font-size: 14px; font-weight: 600; color: var(--text); letter-spacing: -0.2px; }
.topbar-mode {
    font-size: 10px; font-weight: 600; letter-spacing: 1.2px; text-transform: uppercase;
    padding: 3px 8px; border-radius: 2px; border: 1px solid;
}
.topbar-mode.general { color: var(--blue); border-color: rgba(59,130,246,0.3); background: rgba(59,130,246,0.06); }
.topbar-mode.finance { color: var(--green); border-color: rgba(34,197,94,0.3); background: rgba(34,197,94,0.06); }
.topbar-live {
    font-size: 10px; font-weight: 600; letter-spacing: 1.2px; text-transform: uppercase;
    color: var(--accent); border: 1px solid rgba(229,9,20,0.3); background: rgba(229,9,20,0.06);
    padding: 3px 10px; border-radius: 2px; display: flex; align-items: center; gap: 6px;
}
.live-dot {
    width: 5px; height: 5px; border-radius: 50%; background: var(--accent);
    animation: livepulse 1.4s ease-in-out infinite;
}
@keyframes livepulse { 0%,100%{opacity:1} 50%{opacity:0.2} }

.main-glow {
    background: radial-gradient(ellipse at 50% 0%, rgba(229,9,20,0.07) 0%, transparent 65%);
    min-height: 100vh;
    padding-bottom: 120px;
}

.chat-wrap { max-width: 740px; margin: 0 auto; padding: 32px 0 40px; }

.msg-row { display: flex; gap: 12px; margin-bottom: 28px; }
.msg-avatar {
    width: 28px; height: 28px; border-radius: 2px;
    display: flex; align-items: center; justify-content: center;
    font-size: 10px; font-weight: 600; flex-shrink: 0; margin-top: 1px;
    letter-spacing: 0.3px;
}
.avatar-user { background: var(--surface2); color: var(--muted); border: 1px solid var(--border2); }
.avatar-ai { background: var(--accent); color: white; }
.msg-meta { font-size: 10px; font-weight: 600; color: var(--dim); margin-bottom: 6px; letter-spacing: 0.8px; text-transform: uppercase; }
.msg-body { font-size: 14px; line-height: 1.8; color: var(--text); }
.msg-user-bubble { background: var(--surface); border: 1px solid var(--border); padding: 11px 15px; border-radius: var(--radius); display: inline-block; }

.sources-row { display: flex; align-items: center; gap: 6px; margin-top: 10px; flex-wrap: wrap; }
.sources-label { font-size: 9px; color: var(--dim); font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; }
.source-chip { font-size: 10px; font-family: 'JetBrains Mono', monospace; color: var(--blue); background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.2); padding: 2px 7px; border-radius: 2px; }

.disclaimer { margin-top: 12px; padding: 9px 13px; background: rgba(245,158,11,0.05); border-left: 2px solid var(--amber); font-size: 11.5px; color: #92813a; line-height: 1.6; }

.typing-row { display: flex; gap: 4px; align-items: center; padding: 4px 0; }
.typing-dot { width: 5px; height: 5px; background: var(--dim); border-radius: 50%; animation: blink 1.2s infinite; }
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes blink { 0%,60%,100%{opacity:0.2} 30%{opacity:1} }

.input-footer {
    position: fixed; bottom: 0; right: 0; left: 240px; z-index: 90;
    background: linear-gradient(to top, var(--black) 75%, transparent);
    padding: 20px 36px 28px;
}
.input-inner {
    max-width: 740px; margin: 0 auto;
    background: var(--surface); border: 1px solid var(--border2);
    border-radius: var(--radius); display: flex; align-items: flex-end; gap: 8px; padding: 10px 12px;
    transition: border-color 0.15s;
}
.input-inner:focus-within { border-color: #3a3a3a; }

.stTextArea textarea {
    background: transparent !important; border: none !important;
    color: var(--text) !important; font-family: 'Inter', sans-serif !important;
    font-size: 13.5px !important; resize: none !important;
    box-shadow: none !important; padding: 2px 0 !important; line-height: 1.6 !important;
}
.stTextArea textarea::placeholder { color: var(--dim) !important; }
.stTextArea textarea:focus { box-shadow: none !important; border: none !important; outline: none !important; }
.stTextArea [data-baseweb="textarea"] { background: transparent !important; border: none !important; }

.send-btn > button {
    background: var(--text) !important; color: var(--black) !important;
    border: none !important; border-radius: 2px !important;
    font-size: 12px !important; font-weight: 600 !important; padding: 7px 16px !important; letter-spacing: 0.3px !important;
}
.send-btn > button:hover { background: #ccc !important; }

.welcome-wrap {
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; min-height: 55vh; text-align: center;
    padding: 40px 20px 140px;
}
.aria-figure { margin: 0 auto 20px; display: block; }
.aria-intro { font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: var(--dim); margin-bottom: 10px; }
.welcome-title { font-size: 26px; font-weight: 600; letter-spacing: -0.6px; color: var(--text); margin-bottom: 16px; line-height: 1.3; }
.aria-speech {
    font-size: 13.5px; color: var(--muted); line-height: 1.75;
    max-width: 480px; margin: 0 auto 28px; text-align: left;
    background: var(--surface); border: 1px solid var(--border);
    border-left: 2px solid var(--accent); padding: 16px 20px; border-radius: 0 var(--radius) var(--radius) 0;
}
.aria-speech strong { color: var(--text); font-weight: 600; }
.aria-steps { display: flex; gap: 8px; margin-bottom: 32px; max-width: 480px; width: 100%; }
.aria-step { flex: 1; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 12px 14px; text-align: left; }
.aria-step-num { font-size: 9px; font-weight: 600; letter-spacing: 1.5px; color: var(--accent); margin-bottom: 5px; text-transform: uppercase; }
.aria-step-text { font-size: 11.5px; color: var(--muted); line-height: 1.5; }
.aria-step-text strong { color: var(--text); }
.prompts-label { font-size: 9px; font-weight: 600; letter-spacing: 1.8px; text-transform: uppercase; color: var(--dim); margin-bottom: 12px; }
.welcome-card-btn > button {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    color: var(--muted) !important; border-radius: var(--radius) !important;
    padding: 13px 15px !important; font-size: 12.5px !important;
    text-align: left !important; height: auto !important; line-height: 1.5 !important; white-space: normal !important;
}
.welcome-card-btn > button:hover { border-color: var(--border2) !important; color: var(--text) !important; background: var(--surface2) !important; }

.ticker-bar { display: flex; gap: 0; background: var(--bg); border-bottom: 1px solid var(--border); overflow-x: auto; scrollbar-width: none; }
.ticker-bar::-webkit-scrollbar { display: none; }
.ticker-cell { padding: 12px 24px; border-right: 1px solid var(--border); flex-shrink: 0; min-width: 110px; }
.ticker-sym { font-size: 9px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; color: var(--dim); margin-bottom: 3px; }
.ticker-val { font-size: 13px; font-weight: 600; color: var(--text); font-family: 'JetBrains Mono', monospace; letter-spacing: -0.3px; }
.ticker-chg { font-size: 11px; font-family: 'JetBrains Mono', monospace; margin-top: 1px; }
.pos { color: var(--green); }
.neg { color: var(--red); }

.news-page { padding: 0 36px 60px; }
.page-section { margin: 28px 0 14px; font-size: 10px; font-weight: 600; letter-spacing: 1.8px; text-transform: uppercase; color: var(--dim); border-bottom: 1px solid var(--border); padding-bottom: 10px; }

.kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: var(--border); border: 1px solid var(--border); }
.kpi-cell { background: var(--bg); padding: 22px; }
.kpi-label { font-size: 9px; font-weight: 600; letter-spacing: 1.8px; text-transform: uppercase; color: var(--dim); margin-bottom: 10px; }
.kpi-value { font-size: 28px; font-weight: 600; color: var(--text); font-family: 'JetBrains Mono', monospace; letter-spacing: -1.5px; line-height: 1; }
.kpi-change { font-size: 11.5px; font-family: 'JetBrains Mono', monospace; margin-top: 6px; }

.secondary-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1px; background: var(--border); border: 1px solid var(--border); border-top: none; }
.secondary-cell { background: var(--bg); padding: 14px 22px; display: flex; justify-content: space-between; align-items: center; }
.secondary-name { font-size: 12px; font-weight: 400; color: var(--muted); }
.secondary-val { font-size: 12px; font-family: 'JetBrains Mono', monospace; color: var(--text); }

.fg-bar-wrap { position: relative; height: 4px; background: linear-gradient(to right, #ef4444, #f59e0b, #22c55e); margin: 10px 0 6px; }
.fg-marker { position: absolute; top: -4px; width: 12px; height: 12px; background: var(--text); border-radius: 50%; transform: translateX(-50%); border: 2px solid var(--bg); }
.fg-labels { display: flex; justify-content: space-between; font-size: 9px; color: var(--dim); letter-spacing: 0.5px; }

.news-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1px; background: var(--border); border: 1px solid var(--border); }
.news-card { background: var(--bg); padding: 22px; transition: background 0.12s; }
.news-card:hover { background: var(--surface); }
.news-cat { font-size: 9px; font-weight: 600; letter-spacing: 1.8px; text-transform: uppercase; color: var(--accent); margin-bottom: 10px; }
.news-headline { font-size: 14px; font-weight: 600; color: var(--text); line-height: 1.45; margin-bottom: 10px; letter-spacing: -0.2px; }
.news-summary { font-size: 12.5px; color: var(--muted); line-height: 1.65; margin-bottom: 16px; }
.news-meta { display: flex; justify-content: space-between; align-items: center; }
.news-source-name { font-size: 10.5px; font-weight: 600; color: var(--muted); }
.news-date { font-size: 10.5px; color: var(--dim); }
.news-read { font-size: 11px; font-weight: 600; color: var(--blue); text-decoration: none; letter-spacing: 0.3px; }
.news-read:hover { color: #60a5fa; }

.sector-row { display: flex; align-items: center; gap: 12px; padding: 9px 0; border-bottom: 1px solid var(--border); }
.sector-name { font-size: 12px; color: var(--muted); width: 130px; flex-shrink: 0; }
.sector-bar-wrap { flex: 1; height: 3px; background: var(--surface2); position: relative; }
.sector-bar-fill { height: 100%; position: absolute; top: 0; left: 0; }
.sector-pct { font-size: 11px; font-family: 'JetBrains Mono', monospace; width: 54px; text-align: right; flex-shrink: 0; }

.stSelectbox > div > div { background: var(--surface) !important; border: 1px solid var(--border) !important; color: var(--text) !important; border-radius: var(--radius) !important; font-size: 12.5px !important; }
.stFileUploader { background: transparent !important; border: 1px dashed var(--border) !important; border-radius: var(--radius) !important; }
[data-testid="stMarkdownContainer"] p { font-size: 14px; line-height: 1.75; }
</style>
"""

ARIA_SVG_GENERAL = """
<svg width="100" height="130" viewBox="0 0 100 130" fill="none" xmlns="http://www.w3.org/2000/svg" class="aria-figure">
  <circle cx="50" cy="30" r="22" fill="#f5c5a3"/>
  <ellipse cx="50" cy="20" rx="16" ry="10" fill="#1a0f05"/>
  <path d="M34 22 Q50 10 66 22" fill="#1a0f05"/>
  <ellipse cx="50" cy="13" rx="14" ry="6" fill="#1a0f05"/>
  <circle cx="43" cy="32" r="2.5" fill="#3d2b1f"/>
  <circle cx="57" cy="32" r="2.5" fill="#3d2b1f"/>
  <circle cx="44" cy="31" r="0.8" fill="white" opacity="0.7"/>
  <circle cx="58" cy="31" r="0.8" fill="white" opacity="0.7"/>
  <path d="M44 40 Q50 44 56 40" stroke="#c9956a" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <path d="M50 52 L50 52" stroke="#f5c5a3" stroke-width="4"/>
  <path d="M28 56 Q28 48 50 48 Q72 48 72 56 L76 98 Q76 104 50 104 Q24 104 24 98 Z" fill="#1a1a2e"/>
  <path d="M46 48 L42 64 L50 60 L58 64 L54 48" fill="#e8e8e8" opacity="0.92"/>
  <rect x="46" y="60" width="8" height="3" rx="1" fill="#e50914" opacity="0.9"/>
  <rect x="46" y="66" width="8" height="2" rx="1" fill="#e50914" opacity="0.5"/>
  <path d="M28 62 Q16 68 18 84 Q20 96 30 92" fill="#f5c5a3"/>
  <path d="M72 62 Q84 68 82 84 Q80 96 70 92" fill="#f5c5a3"/>
  <path d="M32 118 Q32 104 50 104 Q68 104 68 118" fill="#1a1a2e" opacity="0.7"/>
  <ellipse cx="38" cy="120" rx="7" ry="5" fill="#1a1a2e" opacity="0.6"/>
  <ellipse cx="62" cy="120" rx="7" ry="5" fill="#1a1a2e" opacity="0.6"/>
</svg>
"""

ARIA_SVG_FINANCE = """
<svg width="100" height="130" viewBox="0 0 100 130" fill="none" xmlns="http://www.w3.org/2000/svg" class="aria-figure">
  <circle cx="50" cy="30" r="22" fill="#f5c5a3"/>
  <ellipse cx="50" cy="20" rx="16" ry="10" fill="#0d0a06"/>
  <path d="M34 22 Q50 10 66 22" fill="#0d0a06"/>
  <ellipse cx="50" cy="13" rx="14" ry="6" fill="#0d0a06"/>
  <circle cx="43" cy="32" r="2.5" fill="#2a1e14"/>
  <circle cx="57" cy="32" r="2.5" fill="#2a1e14"/>
  <circle cx="44" cy="31" r="0.8" fill="white" opacity="0.7"/>
  <circle cx="58" cy="31" r="0.8" fill="white" opacity="0.7"/>
  <path d="M44 40 Q50 44 56 40" stroke="#c9956a" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <path d="M28 56 Q28 48 50 48 Q72 48 72 56 L76 98 Q76 104 50 104 Q24 104 24 98 Z" fill="#0f1a0f"/>
  <path d="M46 48 L42 64 L50 60 L58 64 L54 48" fill="#e8e8e8" opacity="0.92"/>
  <rect x="46" y="60" width="8" height="3" rx="1" fill="#22c55e" opacity="0.9"/>
  <rect x="46" y="66" width="8" height="2" rx="1" fill="#22c55e" opacity="0.5"/>
  <path d="M28 62 Q16 68 18 84 Q20 96 30 92" fill="#f5c5a3"/>
  <path d="M72 62 Q84 68 82 84 Q80 96 70 92" fill="#f5c5a3"/>
  <path d="M32 118 Q32 104 50 104 Q68 104 68 118" fill="#0f1a0f" opacity="0.7"/>
  <ellipse cx="38" cy="120" rx="7" ry="5" fill="#0f1a0f" opacity="0.6"/>
  <ellipse cx="62" cy="120" rx="7" ry="5" fill="#0f1a0f" opacity="0.6"/>
</svg>
"""


def init_session():
    defaults = {
        "current_view": "general",
        "active_conv_id": None,
        "pending_suggestion": None,
        "docs_ingested": False,
        "uploaded_names": [],
        "rename_conv_id": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def ingest_startup_docs():
    if not st.session_state.docs_ingested:
        try:
            from config.settings import DOCS_PATH
            if os.path.exists(DOCS_PATH) and os.listdir(DOCS_PATH):
                ingest_directory(DOCS_PATH)
        except Exception:
            pass
        st.session_state.docs_ingested = True


def render_sidebar():
    with st.sidebar:
        st.markdown(
            '<div class="s-wordmark">'
            '<div class="s-wordmark-name">Aria</div>'
            '<div class="s-wordmark-sub">Intelligence Platform</div>'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown('<div class="s-section-label">Navigate</div>', unsafe_allow_html=True)
        for view_id, label in [("general", "General Chat"), ("finance", "Finance Mode"), ("news", "Market News")]:
            if st.button(label, key="nav_" + view_id, use_container_width=True):
                st.session_state.current_view = view_id
                st.session_state.rename_conv_id = None
                st.rerun()

        if st.session_state.current_view in ("general", "finance"):
            mode = st.session_state.current_view

            st.markdown('<div class="s-section-label">Conversations</div>', unsafe_allow_html=True)
            if st.button("+ New Chat", key="new_chat", use_container_width=True):
                cid = create_conversation("New Chat", mode)
                st.session_state.active_conv_id = cid
                st.session_state.rename_conv_id = None
                st.rerun()

            all_convs = get_conversations()
            convs = [c for c in all_convs if c.get("mode", "general") == mode]

            for conv in convs[:18]:
                cid = conv["id"]
                is_active = cid == st.session_state.active_conv_id
                is_pinned = bool(conv.get("pinned", 0))
                raw_title = conv.get("title", "Untitled")
                is_renaming = st.session_state.rename_conv_id == cid

                if is_renaming:
                    new_name = st.text_input(
                        "Rename", value=raw_title,
                        key="rename_input_" + cid,
                        label_visibility="collapsed"
                    )
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        if st.button("Save", key="rename_save_" + cid, use_container_width=True):
                            if new_name.strip():
                                update_conversation_title(cid, new_name.strip())
                            st.session_state.rename_conv_id = None
                            st.rerun()
                    with c2:
                        if st.button("Cancel", key="rename_cancel_" + cid, use_container_width=True):
                            st.session_state.rename_conv_id = None
                            st.rerun()
                else:
                    display = (raw_title[:22] + "…") if len(raw_title) > 22 else raw_title
                    pin_mark = "· " if is_pinned else "  "
                    prefix = "— " if is_active else "  "
                    c1, c2, c3, c4 = st.columns([5, 1, 1, 1])
                    with c1:
                        if st.button(prefix + pin_mark + display, key="conv_" + cid, use_container_width=True):
                            st.session_state.active_conv_id = cid
                            st.session_state.rename_conv_id = None
                            st.rerun()
                    with c2:
                        pin_lbl = "u" if is_pinned else "p"
                        if st.button(pin_lbl, key="pin_" + cid, help="Unpin" if is_pinned else "Pin"):
                            toggle_pin(cid)
                            st.rerun()
                    with c3:
                        if st.button("r", key="ren_" + cid, help="Rename"):
                            st.session_state.rename_conv_id = cid
                            st.rerun()
                    with c4:
                        if st.button("x", key="del_" + cid, help="Delete"):
                            delete_conversation(cid)
                            if st.session_state.active_conv_id == cid:
                                st.session_state.active_conv_id = None
                            st.rerun()

            st.markdown('<div class="s-section-label">Documents</div>', unsafe_allow_html=True)
            uploaded = st.file_uploader(
                "Upload", type=["pdf", "txt", "md"],
                accept_multiple_files=True, key="file_upload",
                label_visibility="collapsed"
            )
            if uploaded:
                for uf in uploaded:
                    if uf.name not in st.session_state.uploaded_names:
                        with st.spinner("Indexing " + uf.name + "…"):
                            n = ingest_bytes(uf.read(), uf.name)
                        st.session_state.uploaded_names.append(uf.name)
                        st.success(uf.name + " — " + str(n) + " chunks")

            sources = list_sources()
            if sources:
                count_line = str(get_doc_count()) + " chunks · " + str(len(sources)) + " file(s)"
                st.markdown(
                    '<div style="font-size:10px;color:var(--dim);padding:4px 0 6px;">' + count_line + '</div>',
                    unsafe_allow_html=True
                )
                for s in sources[:6]:
                    st.markdown('<span class="doc-pill">' + s[:24] + '</span>', unsafe_allow_html=True)


def build_aria_welcome(mode):
    svg = ARIA_SVG_FINANCE if mode == "finance" else ARIA_SVG_GENERAL

    if mode == "finance":
        title = "Finance Intelligence"
        speech = (
            "I'm <strong>Aria</strong>, your finance intelligence assistant. "
            "I walk you through investing fundamentals, explain market mechanics, "
            "break down financial statements, and help you understand risk. "
            "I reference your uploaded documents when relevant, and I always "
            "flag when something is educational context rather than personal advice."
        )
        steps = [
            ("01", "Upload a document", "Drop a PDF or report in the sidebar to ground my answers."),
            ("02", "Ask anything", "Markets, valuation, macro, crypto — broad or specific."),
            ("03", "Follow up", "I remember the conversation. Push back, go deeper, iterate."),
        ]
    else:
        title = "How can I help?"
        speech = (
            "I'm <strong>Aria</strong>, your general-purpose AI assistant. "
            "I help you write, code, research, analyse, and think through problems. "
            "Upload documents and I'll work from them directly. "
            "I'm direct, I don't pad answers, and I'll tell you when I don't know something."
        )
        steps = [
            ("01", "Start a chat", "Hit '+ New Chat' in the sidebar or pick a prompt below."),
            ("02", "Upload context", "Add PDFs or text files — I'll reference them in answers."),
            ("03", "Iterate", "Multi-turn memory is on. Build on previous answers freely."),
        ]

    steps_parts = []
    for num, heading, detail in steps:
        steps_parts.append(
            '<div class="aria-step">'
            '<div class="aria-step-num">' + num + '</div>'
            '<div class="aria-step-text"><strong>' + heading + '</strong><br>' + detail + '</div>'
            '</div>'
        )
    steps_html = "".join(steps_parts)

    html = (
        '<div class="welcome-wrap">'
        '<div class="aria-intro">Your assistant</div>'
        + svg +
        '<div class="welcome-title">' + title + '</div>'
        '<div class="aria-speech">' + speech + '</div>'
        '<div class="aria-steps">' + steps_html + '</div>'
        '<div class="prompts-label">Or start with a prompt</div>'
        '</div>'
    )
    return html


def handle_chat(mode):
    system_prompt = FINANCE_SYSTEM_PROMPT if mode == "finance" else GENERAL_SYSTEM_PROMPT

    if not st.session_state.active_conv_id:
        if mode == "finance":
            suggestions = [
                "Explain the P/E ratio and how investors use it",
                "What is dollar-cost averaging?",
                "How do central bank interest rates affect equity markets?",
                "Explain risk-adjusted return and the Sharpe ratio",
            ]
        else:
            suggestions = [
                "Explain how transformers work in machine learning",
                "Help me write a professional executive summary",
                "Write a Python script to parse a CSV file",
                "Compare REST vs GraphQL APIs",
            ]

        st.markdown(build_aria_welcome(mode), unsafe_allow_html=True)

        cols = st.columns(2)
        for i, text in enumerate(suggestions):
            with cols[i % 2]:
                st.markdown('<div class="welcome-card-btn">', unsafe_allow_html=True)
                if st.button(text, key="sug_" + str(i), use_container_width=True):
                    cid = create_conversation(text[:45], mode)
                    st.session_state.active_conv_id = cid
                    st.session_state.pending_suggestion = text
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        return

    cid = st.session_state.active_conv_id
    conv = get_conversation(cid)
    if not conv:
        st.session_state.active_conv_id = None
        st.rerun()
        return

    messages = get_messages(cid)

    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    if not messages and not st.session_state.get("pending_suggestion"):
        st.markdown(
            '<div style="padding:48px 0;text-align:center;color:var(--dim);font-size:13px;">Send a message to begin.</div>',
            unsafe_allow_html=True
        )
    else:
        render_messages(messages, mode)
    st.markdown('</div>', unsafe_allow_html=True)

    pending = st.session_state.get("pending_suggestion")
    if pending:
        st.session_state.pending_suggestion = None
        process_query(pending, cid, mode, system_prompt)
        st.rerun()

    st.markdown('<div class="input-footer"><div class="input-inner">', unsafe_allow_html=True)
    col1, col2 = st.columns([11, 1])
    with col1:
        placeholder = "Ask about markets, investing, finance…" if mode == "finance" else "Ask anything…"
        user_input = st.text_area(
            "Message", placeholder=placeholder, key="chat_input",
            height=52, label_visibility="collapsed"
        )
    with col2:
        st.markdown('<div class="send-btn">', unsafe_allow_html=True)
        send = st.button("Send", key="send_btn")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    if send and user_input.strip():
        process_query(user_input.strip(), cid, mode, system_prompt)
        st.rerun()


def render_messages(messages, mode):
    for msg in messages:
        role = msg["role"]
        content = msg.get("content", "")
        if role == "user":
            html = (
                '<div class="msg-row">'
                '<div class="msg-avatar avatar-user">YOU</div>'
                '<div>'
                '<div class="msg-meta">You</div>'
                '<div class="msg-body msg-user-bubble">' + content + '</div>'
                '</div>'
                '</div>'
            )
            st.markdown(html, unsafe_allow_html=True)
        else:
            sources = msg.get("sources", [])
            has_disclaimer = "Disclaimer" in content or "not financial advice" in content.lower()
            clean = content.split("---")[0].strip() if "---\n" in content else content

            sources_html = ""
            if sources:
                chips = "".join('<span class="source-chip">' + s + '</span>' for s in sources)
                sources_html = '<div class="sources-row"><span class="sources-label">Sources</span>' + chips + '</div>'

            disclaimer_html = ""
            if mode == "finance" and not has_disclaimer:
                disclaimer_html = (
                    '<div class="disclaimer">For educational purposes only. '
                    'This is not financial advice. Consult a qualified financial advisor '
                    'before making investment decisions.</div>'
                )

            html = (
                '<div class="msg-row">'
                '<div class="msg-avatar avatar-ai">AI</div>'
                '<div style="flex:1;min-width:0">'
                '<div class="msg-meta">Aria</div>'
                '<div class="msg-body">' + clean + '</div>'
                + sources_html + disclaimer_html +
                '</div>'
                '</div>'
            )
            st.markdown(html, unsafe_allow_html=True)


def process_query(query, cid, mode, system_prompt):
    safe, reason = is_safe(query)
    if not safe:
        add_message(cid, "user", query)
        add_message(cid, "assistant", get_refusal_message(reason))
        conv = get_conversation(cid)
        if conv and conv.get("title") == "New Chat":
            update_conversation_title(cid, query[:45])
        return

    add_message(cid, "user", query)

    context, sources = None, []
    if get_doc_count() > 0:
        results = retrieve(query)
        if results:
            context, sources = format_context(results)

    history = get_recent_messages_for_llm(cid, max_messages=18)
    history = history[:-1] if history and history[-1]["role"] == "user" else history
    llm_messages = build_messages(history, query, context=context)

    ph = st.empty()
    ph.markdown(
        '<div class="msg-row">'
        '<div class="msg-avatar avatar-ai">AI</div>'
        '<div><div class="msg-meta">Aria</div>'
        '<div class="typing-row">'
        '<div class="typing-dot"></div>'
        '<div class="typing-dot"></div>'
        '<div class="typing-dot"></div>'
        '</div></div></div>',
        unsafe_allow_html=True
    )

    full = ""
    try:
        for chunk in stream_response(llm_messages, system_prompt):
            full += chunk
            ph.markdown(
                '<div class="msg-row">'
                '<div class="msg-avatar avatar-ai">AI</div>'
                '<div style="flex:1;min-width:0">'
                '<div class="msg-meta">Aria</div>'
                '<div class="msg-body">' + full + '▌</div>'
                '</div></div>',
                unsafe_allow_html=True
            )
    except Exception as e:
        full = "An error occurred: " + str(e)

    ph.empty()

    evaluation = evaluate_response(query, full, sources)
    if not evaluation["passed"] and "contains_error" in evaluation.get("issues", []):
        full += "\n\n*Response quality check flagged an issue.*"

    add_message(cid, "assistant", full, sources=sources)
    conv = get_conversation(cid)
    if conv and conv.get("title") == "New Chat":
        update_conversation_title(cid, query[:45])


def render_news():
    market_data = fetch_market_data()
    indices = market_data.get("indices", [])
    crypto = market_data.get("crypto", [])
    forex = market_data.get("forex", [])
    commodities = market_data.get("commodities", [])

    ticker_parts = ['<div class="ticker-bar">']
    for item in indices + crypto[:2]:
        chg = item["change"]
        sign = "+" if chg >= 0 else ""
        cls = "pos" if chg >= 0 else "neg"
        ticker_parts.append(
            '<div class="ticker-cell">'
            '<div class="ticker-sym">' + item["symbol"] + '</div>'
            '<div class="ticker-val">' + "{:,.2f}".format(item["value"]) + '</div>'
            '<div class="ticker-chg ' + cls + '">' + sign + "{:.2f}".format(chg) + '%</div>'
            '</div>'
        )
    ticker_parts.append('</div>')
    st.markdown("".join(ticker_parts), unsafe_allow_html=True)

    st.markdown('<div class="news-page">', unsafe_allow_html=True)
    st.markdown('<div class="page-section">Market Overview</div>', unsafe_allow_html=True)

    fg = fetch_fear_greed()
    fg_label = next((l for t, l in [(20,"Extreme Fear"),(40,"Fear"),(60,"Neutral"),(80,"Greed"),(100,"Extreme Greed")] if fg <= t), "Greed")
    fg_cls = "pos" if fg >= 50 else "neg"

    kpi_items = [
        ("S&P 500", "{:,.2f}".format(indices[0]["value"]), indices[0]["change"], True),
        ("Nasdaq", "{:,.2f}".format(indices[1]["value"]), indices[1]["change"], True),
        ("Bitcoin", "${:,.0f}".format(crypto[0]["value"]), crypto[0]["change"], True),
        ("Fear & Greed", str(fg), None, False),
    ]
    kpi_parts = ['<div class="kpi-row">']
    for label, val, chg, is_num in kpi_items:
        if is_num and chg is not None:
            sign = "+" if chg >= 0 else ""
            cls = "pos" if chg >= 0 else "neg"
            chg_html = '<div class="kpi-change ' + cls + '">' + sign + "{:.2f}".format(chg) + '%</div>'
        else:
            chg_html = '<div class="kpi-change ' + fg_cls + '">' + fg_label + '</div>'
        kpi_parts.append(
            '<div class="kpi-cell">'
            '<div class="kpi-label">' + label + '</div>'
            '<div class="kpi-value">' + val + '</div>'
            + chg_html +
            '</div>'
        )
    kpi_parts.append('</div>')
    st.markdown("".join(kpi_parts), unsafe_allow_html=True)

    sec_parts = ['<div class="secondary-row">']
    for item in commodities:
        chg = item["change"]
        sign = "+" if chg >= 0 else ""
        cls = "pos" if chg >= 0 else "neg"
        sec_parts.append(
            '<div class="secondary-cell">'
            '<span class="secondary-name">' + item["name"] + '</span>'
            '<span class="secondary-val ' + cls + '">' + sign + "{:.2f}".format(chg) + '%</span>'
            '</div>'
        )
    sec_parts.append('</div>')
    st.markdown("".join(sec_parts), unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown('<div class="page-section">Sector Performance</div>', unsafe_allow_html=True)
        sectors = fetch_sector_performance()
        try:
            import plotly.graph_objects as go
            colors = ["#22c55e" if s["change"] >= 0 else "#ef4444" for s in sectors]
            fig = go.Figure(go.Bar(
                x=[s["change"] for s in sectors],
                y=[s["sector"] for s in sectors],
                orientation="h",
                marker_color=colors,
                marker_line_width=0,
                text=[("+" if s["change"] >= 0 else "") + "{:.2f}".format(s["change"]) + "%" for s in sectors],
                textposition="outside",
                textfont=dict(family="JetBrains Mono", size=10, color="#888"),
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#666", size=11),
                height=300, margin=dict(l=0, r=50, t=0, b=0),
                xaxis=dict(gridcolor="#1f1f1f", zeroline=True, zerolinecolor="#2a2a2a",
                           tickfont=dict(family="JetBrains Mono", size=10)),
                yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=11, color="#888")),
                showlegend=False, bargap=0.35,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        except ImportError:
            for s in sectors:
                chg = s["change"]
                pct = min(abs(chg) / 2.0 * 100, 100)
                fill_color = "#22c55e" if chg >= 0 else "#ef4444"
                sign = "+" if chg >= 0 else ""
                cls = "pos" if chg >= 0 else "neg"
                st.markdown(
                    '<div class="sector-row">'
                    '<div class="sector-name">' + s["sector"] + '</div>'
                    '<div class="sector-bar-wrap">'
                    '<div class="sector-bar-fill" style="width:' + str(pct) + '%;background:' + fill_color + ';opacity:0.7"></div>'
                    '</div>'
                    '<div class="sector-pct ' + cls + '">' + sign + "{:.2f}".format(chg) + '%</div>'
                    '</div>',
                    unsafe_allow_html=True
                )

    with col_right:
        st.markdown('<div class="page-section">Fear & Greed Index</div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="background:var(--bg);border:1px solid var(--border);padding:22px;">'
            '<div style="font-size:42px;font-weight:600;font-family:\'JetBrains Mono\',monospace;letter-spacing:-2px;color:var(--text);line-height:1">' + str(fg) + '</div>'
            '<div style="font-size:12px;font-weight:600;margin:6px 0 16px;letter-spacing:0.5px;" class="' + fg_cls + '">' + fg_label.upper() + '</div>'
            '<div class="fg-bar-wrap"><div class="fg-marker" style="left:' + str(fg) + '%"></div></div>'
            '<div class="fg-labels"><span>Extreme Fear</span><span>Extreme Greed</span></div>'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown('<div class="page-section" style="margin-top:24px">Forex</div>', unsafe_allow_html=True)
        for item in forex:
            chg = item["change"]
            sign = "+" if chg >= 0 else ""
            cls = "pos" if chg >= 0 else "neg"
            st.markdown(
                '<div class="secondary-cell" style="border:1px solid var(--border);border-top:none;background:var(--bg);padding:12px 16px">'
                '<span class="secondary-name">' + item["name"] + '</span>'
                '<div style="text-align:right">'
                '<div style="font-family:\'JetBrains Mono\',monospace;font-size:12px;color:var(--text)">' + str(item["value"]) + '</div>'
                '<div class="' + cls + '" style="font-size:10.5px;font-family:\'JetBrains Mono\',monospace">' + sign + "{:.2f}".format(chg) + '%</div>'
                '</div>'
                '</div>',
                unsafe_allow_html=True
            )

    try:
        import plotly.graph_objects as go
        sparkline = fetch_sparkline_data()
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            y=sparkline, mode="lines", fill="tozeroy",
            line=dict(color="#3b82f6", width=1.5),
            fillcolor="rgba(59,130,246,0.05)",
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=70,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            showlegend=False,
        )
        st.markdown(
            '<div style="margin-top:24px;font-size:9px;font-weight:600;letter-spacing:1.8px;text-transform:uppercase;color:var(--dim);padding-bottom:8px">S&P 500 — 30-Day</div>',
            unsafe_allow_html=True
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    except ImportError:
        pass

    st.markdown('<div class="page-section" style="margin-top:8px">Latest News</div>', unsafe_allow_html=True)
    articles = fetch_news(page_size=12)

    news_parts = ['<div class="news-grid">']
    for article in articles:
        title = (article.get("title") or "").replace("<", "&lt;")
        desc = article.get("description") or ""
        desc = (desc[:130] + "…") if len(desc) > 130 else desc
        desc = desc.replace("<", "&lt;")
        url = article.get("url", "#")
        source = article.get("source", {})
        source_name = source.get("name", "Unknown") if isinstance(source, dict) else str(source)
        cat = article.get("category", "markets").upper().replace("_", " ")
        pub = article.get("publishedAt", "")[:10]
        news_parts.append(
            '<div class="news-card">'
            '<div class="news-cat">' + cat + '</div>'
            '<div class="news-headline">' + title + '</div>'
            '<div class="news-summary">' + desc + '</div>'
            '<div class="news-meta">'
            '<div><span class="news-source-name">' + source_name + '</span>'
            ' <span class="news-date">' + pub + '</span></div>'
            '<a href="' + url + '" target="_blank" class="news-read">Read</a>'
            '</div>'
            '</div>'
        )
    news_parts.append('</div>')
    st.markdown("".join(news_parts), unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def main():
    init_session()
    ingest_startup_docs()

    st.markdown(CSS, unsafe_allow_html=True)

    render_sidebar()

    view = st.session_state.current_view

    st.markdown('<div class="main-glow">', unsafe_allow_html=True)

    if view == "news":
        st.markdown(
            '<div class="topbar">'
            '<div class="topbar-left"><div class="topbar-title">Market News & Analytics</div></div>'
            '<div class="topbar-live"><div class="live-dot"></div>Live</div>'
            '</div>',
            unsafe_allow_html=True
        )
        render_news()

    elif view == "finance":
        st.markdown(
            '<div class="topbar">'
            '<div class="topbar-left">'
            '<div class="topbar-title">Finance Mode</div>'
            '<div class="topbar-mode finance">Finance</div>'
            '</div></div>',
            unsafe_allow_html=True
        )
        handle_chat("finance")

    else:
        st.markdown(
            '<div class="topbar">'
            '<div class="topbar-left">'
            '<div class="topbar-title">General Chat</div>'
            '<div class="topbar-mode general">General</div>'
            '</div></div>',
            unsafe_allow_html=True
        )
        handle_chat("general")

    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()