from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OLLAMA_URL: str = "http://localhost:11434"
    MODEL_NAME: str = "llama3"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 512

settings = Settings()