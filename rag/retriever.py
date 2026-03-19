import numpy as np
from rag.embedder import get_embedding
from rag.vector_store import load_index

def retrieve(query, k=3):
    index, docs = load_index()

    q_emb = np.array([get_embedding(query)])
    distances, indices = index.search(q_emb, k)

    return [docs[i] for i in indices[0]]