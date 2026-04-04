from sentence_transformers import SentenceTransformer
from config.settings import EMBEDDING_MODEL

_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed_texts(texts: list) -> list:
    model = get_model()
    return model.encode(texts, show_progress_bar=False).tolist()


def embed_query(query: str) -> list:
    model = get_model()
    return model.encode([query], show_progress_bar=False)[0].tolist()