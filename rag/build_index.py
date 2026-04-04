from rag.ingestion import ingest_directory
from rag.vector_store import clear_index, get_doc_count
from config.settings import DOCS_PATH


def build_index(clear_existing=False):
    if clear_existing:
        clear_index()
    total = ingest_directory(DOCS_PATH)
    print(f"Index built: {total} chunks from {DOCS_PATH}")
    return total


if __name__ == "__main__":
    build_index(clear_existing=True)
    print(f"Total chunks indexed: {get_doc_count()}")