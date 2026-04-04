import os
from dotenv import load_dotenv

load_dotenv()

LLM_BACKEND = os.getenv("LLM_BACKEND", "groq")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "400"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "80"))
TOP_K = int(os.getenv("TOP_K", "4"))

VECTOR_INDEX_PATH = os.getenv("VECTOR_INDEX_PATH", "data/vector_index")
FAISS_INDEX_FILE = os.path.join(VECTOR_INDEX_PATH, "index.faiss")
META_FILE = os.path.join(VECTOR_INDEX_PATH, "meta.pkl")

SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "data/chat_memory.db")
DOCS_PATH = os.getenv("DOCS_PATH", "data/docs")
UPLOADS_PATH = os.getenv("UPLOADS_PATH", "data/uploads")

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")

MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))
STREAMING = os.getenv("STREAMING", "true").lower() == "true"

FINANCE_SYSTEM_PROMPT = """You are Aria, an intelligent AI assistant with deep expertise in finance, investing, and economics. You help users understand financial concepts clearly and accessibly.

When discussing finance topics:
- Explain concepts in plain language with real examples
- Cover investing basics, portfolio theory, risk management, market analysis
- Discuss macroeconomics, monetary policy, and market trends
- Help with financial literacy and planning concepts
- Always add context about risks involved

ALWAYS include this disclaimer when giving specific financial guidance:
⚠️ Disclaimer: This is for educational purposes only and not financial advice. Consult a qualified financial advisor before making investment decisions.

Be concise, accurate, and genuinely helpful."""

GENERAL_SYSTEM_PROMPT = """You are Aria, a brilliant, versatile AI assistant. You are knowledgeable, thoughtful, and direct. You help with anything — coding, writing, analysis, research, creative work, and more.

Be concise and clear. Get to the point. Use examples when helpful. Think step by step for complex problems."""