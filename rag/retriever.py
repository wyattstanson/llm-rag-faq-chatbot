

from typing import List


class Retriever:
    def __init__(self, vector_store, embedder):
        self.vs = vector_store
        self.embedder = embedder

    def retrieve(self, query: str, top_k: int = 4) -> List[dict]:
        """Embed query and return top-k relevant chunks."""
        if not query.strip():
            return []

        q_emb = self.embedder.embed(query)
        results = self.vs.search(q_emb, top_k=top_k)

        return [r for r in results if r["score"] > 0.2]