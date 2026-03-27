
import os
import json
import pickle
from pathlib import Path
from typing import List, Optional
import numpy as np


class VectorStore:
    def __init__(self, store_path: str):
        self.store_path = Path(store_path)
        self.index_file = self.store_path / "index.faiss"
        self.meta_file = self.store_path / "metadata.pkl"
        self._index = None
        self._texts: List[str] = []
        self._metadata: List[dict] = []

        if self.exists():
            self.load()

    def exists(self) -> bool:
        return self.index_file.exists() and self.meta_file.exists()

    def _get_faiss(self):
        try:
            import faiss
            return faiss
        except ImportError:
            raise ImportError("Run: pip install faiss-cpu")

    def add(
        self,
        embeddings: np.ndarray,
        texts: List[str],
        metadata: Optional[List[dict]] = None,
    ):
        faiss = self._get_faiss()
        embeddings = embeddings.astype(np.float32)
        dim = embeddings.shape[1]

        if self._index is None:
            self._index = faiss.IndexFlatIP(dim)  

        self._index.add(embeddings)
        self._texts.extend(texts)
        self._metadata.extend(metadata or [{} for _ in texts])

    def search(self, query_embedding: np.ndarray, top_k: int = 4) -> List[dict]:
        if self._index is None or self._index.ntotal == 0:
            return []

        q = query_embedding.astype(np.float32).reshape(1, -1)
        k = min(top_k, self._index.ntotal)
        scores, indices = self._index.search(q, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self._texts):
                results.append({
                    "text": self._texts[idx],
                    "score": float(score),
                    "source": self._metadata[idx].get("source", ""),
                    "metadata": self._metadata[idx],
                })
        return results

    def save(self):
        faiss = self._get_faiss()
        self.store_path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(self.index_file))
        with open(self.meta_file, "wb") as f:
            pickle.dump({"texts": self._texts, "metadata": self._metadata}, f)

    def load(self):
        faiss = self._get_faiss()
        self._index = faiss.read_index(str(self.index_file))
        with open(self.meta_file, "rb") as f:
            data = pickle.load(f)
        self._texts = data.get("texts", [])
        self._metadata = data.get("metadata", [])

    @property
    def size(self) -> int:
        return self._index.ntotal if self._index else 0