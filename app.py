

import streamlit as st
import time
import json
import os
from datetime import datetime
from pathlib import Path
import uuid


from config.settings import settings
from llm.client import LLMClient
from llm.prompt_builder import PromptBuilder
from rag.retriever import Retriever
from rag.embedder import Embedder
from rag.vector_store import VectorStore
from rag.ingestion import ingest_documents
from memory.chat_memory import ChatMemory
from rai.intent_classifier import IntentClassifier
from rai.policy_engine import PolicyEngine
from rai.evaluator import ResponseEvaluator


st.set_page_config(
    page_title="FinanceAI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css():
    st.markdown("""
    <style>
    /* ── Import fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

    /* ── Root variables ── */
    :root {
        --bg-primary: #0d0f12;
        --bg-secondary: #13161b;
        --bg-tertiary: #1a1e26;
        --bg-card: #1e2330;
        --border: #2a2f3d;
        --border-light: #353b4d;
        --accent: #4f8ef7;
        --accent-dim: rgba(79,142,247,0.12);
        --accent-glow: rgba(79,142,247,0.25);
        --green: #34d399;
        --red: #f87171;
        --amber: #fbbf24;
        --text-primary: #e8eaf0;
        --text-secondary: #8b919e;
        --text-dim: #545b6b;
        --user-bubble: #1e2d4a;
        --user-border: #2a4070;
        --radius: 14px;
        --radius-sm: 8px;
    }

  
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}
    .block-container {padding: 0 !important; max-width: 100% !important;}

   
    html, body, [data-testid="stAppViewContainer"] {
        background: var(--bg-primary) !important;
        font-family: 'DM Sans', sans-serif;
        color: var(--text-primary);
    }


    [data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border) !important;
        width: 280px !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding: 0 !important;
    }

    .sidebar-logo {
        padding: 20px 18px 16px;
        border-bottom: 1px solid var(--border);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .sidebar-logo-icon {
        width: 32px; height: 32px;
        background: linear-gradient(135deg, var(--accent), #7c6af7);
        border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        font-size: 16px;
    }
    .sidebar-logo-text {
        font-size: 15px; font-weight: 600;
        color: var(--text-primary);
        letter-spacing: -0.3px;
    }
    .sidebar-logo-badge {
        font-size: 10px; color: var(--accent);
        background: var(--accent-dim);
        padding: 2px 7px; border-radius: 10px;
        font-weight: 500; margin-left: auto;
    }


    .new-chat-btn {
        margin: 12px 14px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        padding: 9px 14px;
        cursor: pointer;
        display: flex; align-items: center; gap: 8px;
        color: var(--text-secondary);
        font-size: 13px; font-weight: 500;
        transition: all 0.15s;
        width: calc(100% - 28px);
    }
    .new-chat-btn:hover {
        background: var(--bg-card);
        color: var(--text-primary);
        border-color: var(--border-light);
    }

   
    .conv-section-label {
        padding: 12px 18px 6px;
        font-size: 10px; font-weight: 600;
        text-transform: uppercase; letter-spacing: 1px;
        color: var(--text-dim);
    }
    .conv-item {
        margin: 2px 8px;
        padding: 9px 12px;
        border-radius: var(--radius-sm);
        cursor: pointer;
        display: flex; align-items: center; gap: 9px;
        transition: background 0.12s;
    }
    .conv-item:hover { background: var(--bg-tertiary); }
    .conv-item.active { background: var(--accent-dim); border: 1px solid var(--accent-glow); }
    .conv-item-icon { font-size: 13px; opacity: 0.6; }
    .conv-item-text {
        flex: 1; min-width: 0;
        font-size: 13px; color: var(--text-secondary);
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .conv-item.active .conv-item-text { color: var(--text-primary); }
    .conv-item-time {
        font-size: 10px; color: var(--text-dim);
        white-space: nowrap;
    }


    .chat-wrapper {
        display: flex;
        flex-direction: column;
        height: 100vh;
        background: var(--bg-primary);
    }

  
    .top-bar {
        padding: 14px 28px;
        border-bottom: 1px solid var(--border);
        display: flex; align-items: center; justify-content: space-between;
        background: var(--bg-primary);
        position: sticky; top: 0; z-index: 100;
    }
    .top-bar-title {
        font-size: 14px; font-weight: 600;
        color: var(--text-primary);
    }
    .top-bar-model {
        font-size: 12px; color: var(--text-dim);
        background: var(--bg-tertiary);
        padding: 4px 10px; border-radius: 20px;
        border: 1px solid var(--border);
    }

    
    .messages-container {
        flex: 1;
        overflow-y: auto;
        padding: 28px 0;
    }

    .message-row {
        display: flex;
        padding: 6px 28px;
        max-width: 860px;
        margin: 0 auto;
        width: 100%;
        gap: 14px;
        align-items: flex-start;
    }

    .avatar {
        width: 32px; height: 32px;
        border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        font-size: 14px;
        flex-shrink: 0; margin-top: 2px;
    }
    .avatar-ai {
        background: linear-gradient(135deg, var(--accent), #7c6af7);
    }
    .avatar-user {
        background: var(--user-bubble);
        border: 1px solid var(--user-border);
    }

    .message-content {
        flex: 1; min-width: 0;
        padding-top: 4px;
    }
    .message-sender {
        font-size: 12px; font-weight: 600;
        margin-bottom: 6px;
        color: var(--text-secondary);
        letter-spacing: 0.3px;
    }
    .message-text {
        font-size: 14.5px;
        line-height: 1.75;
        color: var(--text-primary);
    }
    .message-text p { margin: 0 0 10px; }
    .message-text p:last-child { margin-bottom: 0; }
    .message-text code {
        font-family: 'DM Mono', monospace;
        font-size: 13px;
        background: var(--bg-tertiary);
        padding: 2px 6px; border-radius: 4px;
        color: #7dd3fc;
    }
    .message-text pre {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        padding: 14px 16px;
        overflow-x: auto;
        margin: 10px 0;
    }
    .message-text pre code {
        background: none; padding: 0;
        font-size: 13px; color: var(--text-primary);
    }
    .message-text ul, .message-text ol {
        padding-left: 20px; margin: 8px 0;
    }
    .message-text li { margin-bottom: 4px; }
    .message-text strong { color: #c7d2fe; font-weight: 600; }
    .message-text h3 {
        font-size: 15px; font-weight: 600;
        color: var(--text-primary); margin: 14px 0 6px;
    }

 
    .sources-row {
        display: flex; flex-wrap: wrap; gap: 6px;
        margin-top: 10px;
    }
    .source-chip {
        font-size: 11px;
        background: var(--bg-card);
        border: 1px solid var(--border);
        color: var(--text-dim);
        padding: 3px 9px; border-radius: 12px;
        display: flex; align-items: center; gap: 5px;
    }
    .source-chip span { color: var(--accent); }

   
    .disclaimer-badge {
        display: inline-flex; align-items: center; gap: 5px;
        font-size: 11px; color: var(--amber);
        background: rgba(251,191,36,0.08);
        border: 1px solid rgba(251,191,36,0.2);
        padding: 3px 9px; border-radius: 12px;
        margin-top: 8px;
    }

    
    .typing-indicator {
        display: flex; gap: 4px; align-items: center;
        padding: 4px 0;
    }
    .typing-dot {
        width: 6px; height: 6px;
        background: var(--text-dim);
        border-radius: 50%;
        animation: pulse 1.2s ease-in-out infinite;
    }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes pulse {
        0%, 100% { opacity: 0.3; transform: translateY(0); }
        50% { opacity: 1; transform: translateY(-3px); }
    }

  
    .welcome-screen {
        max-width: 620px; margin: 60px auto;
        text-align: center; padding: 0 28px;
    }
    .welcome-icon {
        width: 56px; height: 56px;
        background: linear-gradient(135deg, var(--accent), #7c6af7);
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        font-size: 26px;
        margin: 0 auto 20px;
    }
    .welcome-title {
        font-size: 26px; font-weight: 600;
        color: var(--text-primary); margin-bottom: 10px;
        letter-spacing: -0.5px;
    }
    .welcome-sub {
        font-size: 15px; color: var(--text-secondary);
        line-height: 1.6; margin-bottom: 32px;
    }
    .suggestion-grid {
        display: grid; grid-template-columns: 1fr 1fr;
        gap: 10px; text-align: left;
    }
    .suggestion-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 14px 16px;
        cursor: pointer;
        transition: all 0.15s;
    }
    .suggestion-card:hover {
        border-color: var(--accent);
        background: var(--accent-dim);
    }
    .suggestion-label {
        font-size: 12px; color: var(--accent);
        font-weight: 600; margin-bottom: 4px;
    }
    .suggestion-text {
        font-size: 13px; color: var(--text-secondary);
        line-height: 1.4;
    }

   
    .input-area {
        padding: 16px 28px 20px;
        background: var(--bg-primary);
        border-top: 1px solid var(--border);
        max-width: 860px; margin: 0 auto; width: 100%;
    }
    .input-container {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 12px 14px;
        display: flex; align-items: flex-end; gap: 10px;
        transition: border-color 0.15s;
    }
    .input-container:focus-within {
        border-color: var(--accent);
        box-shadow: 0 0 0 3px var(--accent-dim);
    }


    .stTextArea textarea {
        background: transparent !important;
        border: none !important;
        color: var(--text-primary) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 14.5px !important;
        resize: none !important;
        padding: 0 !important;
        box-shadow: none !important;
    }
    .stTextArea textarea::placeholder { color: var(--text-dim) !important; }
    .stTextArea [data-baseweb="base-input"] {
        background: transparent !important;
        border: none !important;
    }

    
    .stButton > button {
        background: var(--accent) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        padding: 8px 16px !important;
        transition: all 0.15s !important;
    }
    .stButton > button:hover {
        background: #3d7de8 !important;
        transform: translateY(-1px) !important;
    }

    [data-testid="stFileUploader"] {
        background: var(--bg-tertiary) !important;
        border: 1px dashed var(--border) !important;
        border-radius: var(--radius-sm) !important;
    }

    
    .stat-row {
        display: flex; gap: 8px; flex-wrap: wrap;
        margin: 12px 14px;
    }
    .stat-pill {
        font-size: 11px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        color: var(--text-dim);
        padding: 4px 10px; border-radius: 20px;
        display: flex; align-items: center; gap: 5px;
    }
    .stat-pill b { color: var(--text-secondary); }

   
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: var(--border);
        border-radius: 10px;
    }

  
    .refusal-msg {
        background: rgba(248,113,113,0.08);
        border: 1px solid rgba(248,113,113,0.2);
        border-radius: var(--radius-sm);
        padding: 10px 14px;
        color: #fca5a5;
        font-size: 13.5px;
    }

    /* ── Streamlit column gaps ── */
    [data-testid="column"] { padding: 0 !important; }
    </style>
    """, unsafe_allow_html=True)



def init_session():
    if "chat_memory" not in st.session_state:
        st.session_state.chat_memory = ChatMemory(settings.MEMORY_DB_PATH)
    if "current_conv_id" not in st.session_state:
        st.session_state.current_conv_id = None
    if "conversations" not in st.session_state:
        st.session_state.conversations = []
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "retriever" not in st.session_state:
        st.session_state.retriever = None
    if "llm_client" not in st.session_state:
        st.session_state.llm_client = LLMClient()
    if "prompt_builder" not in st.session_state:
        st.session_state.prompt_builder = PromptBuilder()
    if "intent_classifier" not in st.session_state:
        st.session_state.intent_classifier = IntentClassifier()
    if "policy_engine" not in st.session_state:
        st.session_state.policy_engine = PolicyEngine()
    if "evaluator" not in st.session_state:
        st.session_state.evaluator = ResponseEvaluator()
    if "docs_uploaded" not in st.session_state:
        st.session_state.docs_uploaded = []
    if "suggestion_clicked" not in st.session_state:
        st.session_state.suggestion_clicked = None


    st.session_state.conversations = (
        st.session_state.chat_memory.list_conversations()
    )


    _load_vector_store()


def _load_vector_store():
    try:
        vs = VectorStore(settings.VECTOR_STORE_PATH)
        if vs.exists():
            embedder = Embedder(settings.EMBED_MODEL)
            st.session_state.retriever = Retriever(vs, embedder)
    except Exception:
        pass



def render_sidebar():
    with st.sidebar:
        # Logo
        st.markdown("""
        <div class="sidebar-logo">
            <div class="sidebar-logo-icon">📈</div>
            <div class="sidebar-logo-text">FinanceAI</div>
            <div class="sidebar-logo-badge">BETA</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("＋  New Conversation", key="new_chat", use_container_width=True):
            new_id = st.session_state.chat_memory.new_conversation()
            st.session_state.current_conv_id = new_id
            st.session_state.messages = []
            st.session_state.conversations = (
                st.session_state.chat_memory.list_conversations()
            )
            st.rerun()

      
        convs = st.session_state.conversations
        if convs:
            st.markdown('<div class="conv-section-label">Recent Chats</div>',
                        unsafe_allow_html=True)
            for conv in convs[:20]:
                is_active = conv["id"] == st.session_state.current_conv_id
                active_cls = "active" if is_active else ""
                ts = conv.get("updated_at", "")[:10] if conv.get("updated_at") else ""
                label = conv.get("title", "New conversation")[:32]
                btn_key = f"conv_{conv['id']}"
                if st.button(
                    f"{'💬' if is_active else '○'}  {label}",
                    key=btn_key,
                    use_container_width=True
                ):
                    st.session_state.current_conv_id = conv["id"]
                    st.session_state.messages = (
                        st.session_state.chat_memory.load_messages(conv["id"])
                    )
                    st.rerun()

        st.divider()

    
        st.markdown("**📂 Knowledge Base**")
        uploaded = st.file_uploader(
            "Upload PDF or TXT",
            type=["pdf", "txt"],
            accept_multiple_files=True,
            key="doc_upload",
            label_visibility="collapsed"
        )
        if uploaded:
            if st.button("Ingest Documents", use_container_width=True):
                with st.spinner("Processing…"):
                    paths = _save_uploads(uploaded)
                    _ingest(paths)

       
        if st.session_state.docs_uploaded:
            st.markdown(
                '<div class="conv-section-label">Indexed Documents</div>',
                unsafe_allow_html=True
            )
            for doc in st.session_state.docs_uploaded[-8:]:
                st.markdown(
                    f'<div class="stat-pill">📄 <b>{doc[:24]}</b></div>',
                    unsafe_allow_html=True
                )

        st.divider()

       
        model_name = settings.LLM_MODEL or "Not configured"
        backend = settings.LLM_BACKEND
        st.markdown(
            f'<div class="stat-pill">🤖 <b>{backend}</b> · {model_name[:20]}</div>',
            unsafe_allow_html=True
        )
        rag_status = "✅ Active" if st.session_state.retriever else "⚪ No docs"
        st.markdown(
            f'<div class="stat-pill" style="margin-top:6px">📚 RAG: <b>{rag_status}</b></div>',
            unsafe_allow_html=True
        )


def _save_uploads(files) -> list:
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for f in files:
        dest = upload_dir / f.name
        dest.write_bytes(f.read())
        paths.append(str(dest))
        if f.name not in st.session_state.docs_uploaded:
            st.session_state.docs_uploaded.append(f.name)
    return paths


def _ingest(paths: list):
    try:
        embedder = Embedder(settings.EMBED_MODEL)
        vs = VectorStore(settings.VECTOR_STORE_PATH)
        ingest_documents(paths, embedder, vs,
                         chunk_size=settings.CHUNK_SIZE,
                         chunk_overlap=settings.CHUNK_OVERLAP)
        st.session_state.retriever = Retriever(vs, embedder)
        st.success(f"✅ {len(paths)} document(s) indexed!")
    except Exception as e:
        st.error(f"Ingestion error: {e}")



def render_message(role: str, content: str, sources=None, is_typing=False):
    if role == "user":
        avatar = "🧑"
        avatar_cls = "avatar-user"
        sender = "You"
    else:
        avatar = "📈"
        avatar_cls = "avatar-ai"
        sender = "FinanceAI"

    if is_typing:
        body = """
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>"""
    else:
        import re
       
        safe = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
       
        safe = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', safe)
        
        safe = re.sub(r'`([^`]+)`', r'<code>\1</code>', safe)
        
        safe = re.sub(r'^### (.+)$', r'<h3>\1</h3>', safe, flags=re.MULTILINE)
       
        safe = re.sub(r'^\* (.+)$', r'<li>\1</li>', safe, flags=re.MULTILINE)
        safe = re.sub(r'^- (.+)$', r'<li>\1</li>', safe, flags=re.MULTILINE)
        safe = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', safe, flags=re.DOTALL)
       
        parts = safe.split('\n\n')
        parts = [f"<p>{p.replace(chr(10), '<br>')}</p>" if not p.strip().startswith('<') else p
                 for p in parts if p.strip()]
        body = ''.join(parts)

    sources_html = ""
    if sources:
        chips = "".join(
            f'<div class="source-chip"><span>📄</span> {s}</div>'
            for s in sources
        )
        sources_html = f'<div class="sources-row">{chips}</div>'

    disclaimer_html = ""
    if role == "assistant" and content:
        disclaimer_html = """
        <div class="disclaimer-badge">
            ⚠️ Not financial advice. For informational purposes only.
        </div>"""

    st.markdown(f"""
    <div class="message-row">
        <div class="avatar {avatar_cls}">{avatar}</div>
        <div class="message-content">
            <div class="message-sender">{sender}</div>
            <div class="message-text">{body}</div>
            {sources_html}
            {disclaimer_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_welcome():
    suggestions = [
        ("📊 Investing", "What's the difference between stocks, bonds, and ETFs?"),
        ("💰 Budgeting", "How do I create a personal budget using the 50/30/20 rule?"),
        ("📈 Risk", "Explain risk tolerance and how it affects my portfolio"),
        ("🏦 Concepts", "What is compound interest and why does it matter?"),
    ]

    st.markdown("""
    <div class="welcome-screen">
        <div class="welcome-icon">📈</div>
        <div class="welcome-title">Your Finance AI Assistant</div>
        <div class="welcome-sub">
            Ask me anything about investing, financial literacy, budgeting, or risk management.
            Upload your documents for personalized insights.
        </div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(2)
    for i, (label, text) in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(f"{label}\n{text}", key=f"suggest_{i}", use_container_width=True):
                st.session_state.suggestion_clicked = text
                st.rerun()



def process_query(query: str):
    """Run the full RAG + LLM + RAI pipeline."""


    if not st.session_state.current_conv_id:
        cid = st.session_state.chat_memory.new_conversation(title=query[:40])
        st.session_state.current_conv_id = cid
        st.session_state.conversations = (
            st.session_state.chat_memory.list_conversations()
        )
    else:

        if len(st.session_state.messages) == 0:
            st.session_state.chat_memory.update_title(
                st.session_state.current_conv_id, query[:40]
            )

    
    intent = st.session_state.intent_classifier.classify(query)
    allowed, refusal_msg = st.session_state.policy_engine.check(query, intent)

    if not allowed:
        return refusal_msg, [], True  # content, sources, is_refusal


    sources = []
    context_chunks = []
    if st.session_state.retriever:
        results = st.session_state.retriever.retrieve(
            query, top_k=settings.TOP_K
        )
        for r in results:
            context_chunks.append(r["text"])
            src = r.get("source", "")
            if src and src not in sources:
                sources.append(src)

  
    history = st.session_state.messages[-settings.MAX_HISTORY * 2:]
    prompt = st.session_state.prompt_builder.build(
        query=query,
        history=history,
        context_chunks=context_chunks,
        intent=intent
    )

 
    return prompt, sources, False


def stream_response(prompt: str, placeholder):
    """Stream tokens into a Streamlit placeholder."""
    full_text = ""
    try:
        for chunk in st.session_state.llm_client.stream(prompt):
            full_text += chunk
            # Render partial with cursor
            placeholder.markdown(
                full_text + "▌",
                unsafe_allow_html=False
            )
        placeholder.empty()
    except Exception as e:
        full_text = f"⚠️ Error generating response: {str(e)}\n\nPlease check your LLM configuration in `.env`."
        placeholder.empty()
    return full_text



def main():
    load_css()
    init_session()

    
    render_sidebar()

  
    prefill = ""
    if st.session_state.suggestion_clicked:
        prefill = st.session_state.suggestion_clicked
        st.session_state.suggestion_clicked = None

  
    msgs = st.session_state.messages

  
    if not msgs and not st.session_state.current_conv_id:
        render_welcome()
    else:
        st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
        for msg in msgs:
            render_message(
                msg["role"],
                msg["content"],
                sources=msg.get("sources", [])
            )

    st.markdown('<div style="height:80px"></div>', unsafe_allow_html=True)

    
    with st.container():
        st.markdown(
            '<div style="position:fixed;bottom:0;left:280px;right:0;z-index:200;'
            'background:var(--bg-primary,#0d0f12);border-top:1px solid #2a2f3d;'
            'padding:14px 28px 18px;">',
            unsafe_allow_html=True
        )
        col1, col2 = st.columns([10, 1])
        with col1:
            user_input = st.text_area(
                "Message",
                value=prefill,
                placeholder="Ask about investing, markets, financial planning…",
                key="user_input",
                height=52,
                label_visibility="collapsed"
            )
        with col2:
            send = st.button("Send ↑", key="send_btn")
        st.markdown("</div>", unsafe_allow_html=True)

  
    if send and user_input.strip():
        query = user_input.strip()

        
        st.session_state.messages.append({
            "role": "user",
            "content": query,
            "sources": []
        })
        render_message("user", query)

        
        typing_ph = st.empty()
        typing_ph.markdown("""
        <div class="message-row">
            <div class="avatar avatar-ai">📈</div>
            <div class="message-content">
                <div class="message-sender">FinanceAI</div>
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        
        prompt, sources, is_refusal = process_query(query)
        typing_ph.empty()

        if is_refusal:
            response_text = prompt  # refusal message
        else:
           
            stream_ph = st.empty()
            response_text = stream_response(prompt, stream_ph)

        
        render_message("assistant", response_text, sources=sources)

       
        st.session_state.messages.append({
            "role": "assistant",
            "content": response_text,
            "sources": sources
        })
        if st.session_state.current_conv_id:
            st.session_state.chat_memory.save_message(
                st.session_state.current_conv_id, "user", query
            )
            st.session_state.chat_memory.save_message(
                st.session_state.current_conv_id, "assistant", response_text,
                metadata={"sources": sources}
            )

        st.rerun()


if __name__ == "__main__":
   main()