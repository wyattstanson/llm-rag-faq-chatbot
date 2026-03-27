
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    
    LLM_BACKEND: str = os.getenv("LLM_BACKEND", "ollama")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3.2")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://localhost:11434")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "1024"))
    LLM_STREAM: bool = os.getenv("LLM_STREAM", "true").lower() == "true"

    
    EMBED_MODEL: str = os.getenv(
        "EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )

 
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "400"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "80"))
    TOP_K: int = int(os.getenv("TOP_K", "4"))

    
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data" / "docs"
    VECTOR_STORE_PATH: str = str(BASE_DIR / "data" / "vector_store")
    MEMORY_DB_PATH: str = str(BASE_DIR / "data" / "chat_memory.db")
    UPLOAD_DIR: str = str(BASE_DIR / "data" / "uploads")

    MAX_HISTORY: int = int(os.getenv("MAX_HISTORY", "10"))

  
    SYSTEM_PROMPT: str = os.getenv("SYSTEM_PROMPT", """You are FinanceAI, a knowledgeable and professional financial assistant. \
You provide clear, accurate, and educational information about:
- Personal finance and budgeting
- Investing concepts (stocks, bonds, ETFs, mutual funds, crypto)
- Risk management and portfolio theory
- Financial literacy and economic concepts
- Market analysis and financial planning frameworks

Your tone is professional yet approachable — like a knowledgeable friend with a finance background. \
You explain concepts clearly, use real-world examples, and break down complex ideas step-by-step.

IMPORTANT RULES:
1. Always clarify you are NOT providing personalised financial advice
2. Encourage consulting a qualified financial advisor for personal decisions
3. Be balanced when discussing investments — always mention risks alongside rewards
4. Never recommend specific stocks, funds, or timing the market
5. Cite retrieved context when available; be transparent about your sources
6. If you don't know something, say so honestly""")


    ENABLE_RAI: bool = os.getenv("ENABLE_RAI", "true").lower() == "true"
    BLOCKED_INTENTS: list = ["illegal", "manipulation", "harmful", "pii_request"]


settings = Settings()


os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(settings.MEMORY_DB_PATH), exist_ok=True)