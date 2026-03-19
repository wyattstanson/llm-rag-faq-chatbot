import os
from rag.embedder import get_embedding
from rag.vector_store import create_index, save_index

DOC_PATH = "data/docs"

documents = []

for file in os.listdir(DOC_PATH):
    file_path = os.path.join(DOC_PATH, file)
    if os.path.isfile(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            documents.append(f.read())

if len(documents) == 0:
    print("No documents found in data/docs/")
    exit()

embeddings = [get_embedding(doc) for doc in documents]

index = create_index(embeddings)
save_index(index, documents)

print("Index built successfully")