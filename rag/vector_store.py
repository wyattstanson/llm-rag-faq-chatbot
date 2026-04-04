import faiss
import pickle
import numpy as np
import os
from config.settings import VECTOR_INDEX_PATH, FAISS_INDEX_FILE, META_FILE

os.makedirs(VECTOR_INDEX_PATH, exist_ok=True)

_index = None
_metadata = []


def _normalise(m):
    if isinstance(m, dict):
        return m
    if isinstance(m, str):
        return {"text": m, "source": m, "chunk_index": 0}
    return {"text": str(m), "source": "unknown", "chunk_index": 0}


def _load_index(dim=384):
    global _index
    if _index is None:
        if os.path.exists(FAISS_INDEX_FILE):
            _index = faiss.read_index(FAISS_INDEX_FILE)
        else:
            _index = faiss.IndexFlatIP(dim)
    return _index


def _load_metadata():
    global _metadata
    if not _metadata and os.path.exists(META_FILE):
        with open(META_FILE, "rb") as f:
            raw = pickle.load(f)
        _metadata = [_normalise(m) for m in raw]
    return _metadata


def _save():
    faiss.write_index(_index, FAISS_INDEX_FILE)
    with open(META_FILE, "wb") as f:
        pickle.dump(_metadata, f)


def add_vectors(vectors, metadata_list):
    global _index, _metadata
    arr = np.array(vectors, dtype="float32")
    faiss.normalize_L2(arr)
    _load_metadata()
    idx = _load_index(arr.shape[1])
    idx.add(arr)
    _metadata.extend([_normalise(m) for m in metadata_list])
    _save()


def search(query_vector, top_k=4):
    _load_metadata()
    if not _metadata:
        return []
    idx = _load_index()
    arr = np.array([query_vector], dtype="float32")
    faiss.normalize_L2(arr)
    scores, indices = idx.search(arr, min(top_k, len(_metadata)))
    results = []
    for score, i in zip(scores[0], indices[0]):
        if 0 <= i < len(_metadata):
            results.append({**_metadata[i], "score": float(score)})
    return results


def get_doc_count():
    _load_metadata()
    return len(_metadata)


def list_sources():
    _load_metadata()
    seen = set()
    sources = []
    for m in _metadata:
        src = m.get("source", "unknown")
        if src not in seen:
            seen.add(src)
            sources.append(src)
    return sources


def clear_index():
    global _index, _metadata
    _index = None
    _metadata = []
    for f in [FAISS_INDEX_FILE, META_FILE]:
        if os.path.exists(f):
            os.remove(f)