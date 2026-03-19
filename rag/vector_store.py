import faiss
import numpy as np
import os
import pickle

INDEX_PATH = "data/vector_index/index.faiss"
META_PATH = "data/vector_index/meta.pkl"

def create_index(embeddings):
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    return index

def save_index(index, documents):
    os.makedirs("data/vector_index", exist_ok=True)
    faiss.write_index(index, INDEX_PATH)

    with open(META_PATH, "wb") as f:
        pickle.dump(documents, f)

def load_index():
    index = faiss.read_index(INDEX_PATH)

    with open(META_PATH, "rb") as f:
        docs = pickle.load(f)

    return index, docs