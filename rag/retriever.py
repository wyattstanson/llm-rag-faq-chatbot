from rag.embedder import embed_query
from rag.vector_store import search
from config.settings import TOP_K


def retrieve(query, top_k=TOP_K):
    qv = embed_query(query)
    return search(qv, top_k=top_k)


def format_context(results):
    if not results:
        return None, []

    parts = []
    sources = []
    for i, r in enumerate(results):
        parts.append(f"[Source {i+1}: {r.get('source', 'doc')}]\n{r['text']}")
        src = r.get("source", "unknown")
        if src not in sources:
            sources.append(src)

    return "\n\n".join(parts), sources