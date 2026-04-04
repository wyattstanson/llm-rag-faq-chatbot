import re
import os
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP, UPLOADS_PATH, DOCS_PATH

os.makedirs(UPLOADS_PATH, exist_ok=True)
os.makedirs(DOCS_PATH, exist_ok=True)


def chunk_text(text, source="unknown", chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    text = re.sub(r'\s+', ' ', text).strip()
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append({
            "text": chunk,
            "source": source,
            "chunk_index": len(chunks)
        })
        start += chunk_size - overlap
    return chunks


def extract_text(file_bytes=None, file_path=None, filename="unknown"):
    ext = filename.lower().split(".")[-1]
    if ext == "pdf":
        return _extract_pdf(file_bytes=file_bytes, file_path=file_path)
    elif ext in ("txt", "md"):
        if file_bytes:
            return file_bytes.decode("utf-8", errors="ignore")
        with open(file_path, "r", errors="ignore") as f:
            return f.read()
    return ""


def _extract_pdf(file_bytes=None, file_path=None):
    try:
        import pdfplumber
        import io
        src = io.BytesIO(file_bytes) if file_bytes else file_path
        with pdfplumber.open(src) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    except Exception:
        try:
            import PyPDF2
            import io
            src = io.BytesIO(file_bytes) if file_bytes else open(file_path, "rb")
            reader = PyPDF2.PdfReader(src)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            return f"[PDF extraction failed: {e}]"


def ingest_bytes(file_bytes, filename):
    from rag.embedder import embed_texts
    from rag.vector_store import add_vectors

    save_path = os.path.join(UPLOADS_PATH, filename)
    with open(save_path, "wb") as f:
        f.write(file_bytes)

    text = extract_text(file_bytes=file_bytes, filename=filename)
    if not text or len(text.strip()) < 50:
        return 0

    chunks = chunk_text(text, source=filename)
    if not chunks:
        return 0

    vectors = embed_texts([c["text"] for c in chunks])
    add_vectors(vectors, chunks)
    return len(chunks)


def ingest_directory(path=DOCS_PATH):
    from rag.embedder import embed_texts
    from rag.vector_store import add_vectors

    total = 0
    if not os.path.exists(path):
        return total

    for fname in os.listdir(path):
        fpath = os.path.join(path, fname)
        if not os.path.isfile(fpath):
            continue
        text = extract_text(file_path=fpath, filename=fname)
        if not text:
            continue
        chunks = chunk_text(text, source=fname)
        if chunks:
            vectors = embed_texts([c["text"] for c in chunks])
            add_vectors(vectors, chunks)
            total += len(chunks)
    return total