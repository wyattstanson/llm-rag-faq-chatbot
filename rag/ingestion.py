

import re
from pathlib import Path
from typing import List


def load_document(path: str) -> str:
    """Load raw text from a file."""
    p = Path(path)
    suffix = p.suffix.lower()

    if suffix == ".txt" or suffix == ".md":
        return p.read_text(encoding="utf-8", errors="ignore")

    elif suffix == ".pdf":
        try:
            import pdfplumber
            text_parts = []
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        text_parts.append(t)
            return "\n\n".join(text_parts)
        except ImportError:
            # Fallback to PyPDF2
            try:
                import PyPDF2
                text_parts = []
                with open(path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        t = page.extract_text()
                        if t:
                            text_parts.append(t)
                return "\n\n".join(text_parts)
            except ImportError:
                raise ImportError("Install pdfplumber: pip install pdfplumber")
    else:
     
        try:
            return p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            raise ValueError(f"Unsupported file type: {suffix}")


def chunk_text(
    text: str,
    chunk_size: int = 400,
    chunk_overlap: int = 80,
    source: str = ""
) -> List[dict]:
    """
    Split text into overlapping chunks.
    Returns list of dicts with 'text' and 'source' keys.
    """
    
    text = re.sub(r"\n{3,}", "\n\n", text.strip())

    
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        if len(chunk_text.strip()) > 30:  
            chunks.append({
                "text": chunk_text,
                "source": Path(source).name if source else "unknown",
                "chunk_index": len(chunks),
            })

        if end >= len(words):
            break
        start = end - chunk_overlap  

    return chunks


def ingest_documents(
    paths: List[str],
    embedder,
    vector_store,
    chunk_size: int = 400,
    chunk_overlap: int = 80,
):
    """
    Full ingestion pipeline:
    1. Load documents
    2. Chunk text
    3. Embed chunks
    4. Add to vector store
    5. Save vector store
    """
    all_chunks = []

    for path in paths:
        try:
            text = load_document(path)
            chunks = chunk_text(text, chunk_size, chunk_overlap, source=path)
            all_chunks.extend(chunks)
            print(f"  ✓ {Path(path).name} → {len(chunks)} chunks")
        except Exception as e:
            print(f"  ✗ {Path(path).name}: {e}")

    if not all_chunks:
        raise ValueError("No content could be extracted from uploaded files.")

  
    texts = [c["text"] for c in all_chunks]
    embeddings = embedder.embed_batch(texts)

  
    vector_store.add(
        embeddings=embeddings,
        texts=texts,
        metadata=[{"source": c["source"], "chunk_index": c["chunk_index"]}
                  for c in all_chunks],
    )
    vector_store.save()

    print(f"  ✓ Total: {len(all_chunks)} chunks indexed")
    return len(all_chunks)