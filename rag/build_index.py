

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from rag.embedder import Embedder
from rag.vector_store import VectorStore
from rag.ingestion import ingest_documents


def build():
    docs_dir = settings.DATA_DIR
    paths = list(docs_dir.glob("**/*.txt")) + list(docs_dir.glob("**/*.pdf"))

    if not paths:
        print(f"No documents found in {docs_dir}")
        return

    print(f"Found {len(paths)} documents. Building index…")
    embedder = Embedder(settings.EMBED_MODEL)
    vs = VectorStore(settings.VECTOR_STORE_PATH)

    n = ingest_documents(
        [str(p) for p in paths],
        embedder, vs,
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    print(f"Done! {n} chunks indexed → {settings.VECTOR_STORE_PATH}")


if __name__ == "__main__":
    build()