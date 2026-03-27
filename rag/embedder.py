

from typing import List
import numpy as np


class Embedder:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed(self, text: str) -> np.ndarray:
        """Embed a single string."""
        return self.model.encode(text, convert_to_numpy=True, normalize_embeddings=True)

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Embed a list of strings — returns (N, dim) array."""
        return self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=len(texts) > 100,
        )