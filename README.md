# Local LLM RAG Chatbot

A locally running Retrieval-Augmented Generation (RAG) chatbot built using Ollama, FAISS, and Streamlit. The system answers user queries based on custom documents using a modular pipeline.

---

## Features

* Retrieval-Augmented Generation (RAG)
* Local LLM inference using Ollama (LLaMA 3 / Mistral)
* Custom document ingestion
* FAISS-based vector search
* Interactive Streamlit interface
* Basic Responsible AI pipeline (intent classification, policy checks, evaluation)

---

## Project Structure

```
local-llm-rag/
│
├── app.py
├── requirements.txt
│
├── config/
│   └── settings.py
│
├── rag/
│   ├── retriever.py
│   ├── vector_store.py
│   ├── embedder.py
│   └── build_index.py
│
├── llm/
│   ├── client.py
│   └── prompt_builder.py
│
├── memory/
│   └── chat_memory.py
│
├── rai/
│   ├── intent_classifier.py
│   ├── policy_engine.py
│   └── evaluator.py
│
├── data/
│   ├── docs/
│   └── vector_index/
│
└── .gitignore
```

---

## Setup Instructions

### 1. Clone the repository

```
git clone https://github.com/wyattstanson/llm-rag-faq-chatbot.git
cd local-llm-rag
```

---

### 2. Create a virtual environment

```
python -m venv .venv
.venv\Scripts\activate
```

---

### 3. Install dependencies

```
pip install -r requirements.txt
```

---

### 4. Install and run Ollama

Download Ollama from: https://ollama.com

Run a model:

```
ollama run llama3
```

Alternative (lighter model):

```
ollama run mistral
```

---

### 5. Add documents

Place your `.txt` files inside:

```
data/docs/
```

---

### 6. Build vector index

```
python -m rag.build_index
```

---

### 7. Run the application

```
streamlit run app.py
```

---

## Example Workflow

1. Add documents to `data/docs`
2. Build the FAISS index
3. Enter a query in the UI
4. Relevant context is retrieved
5. The LLM generates a grounded response

---

## Tech Stack

* LLM: Ollama (LLaMA 3 / Mistral)
* Vector Database: FAISS
* Embeddings: Sentence Transformers
* Backend: Python
* Frontend: Streamlit

---

## Limitations

* Requires local setup with Ollama running
* Not deployed publicly
* Limited to locally available documents

---

## Future Improvements

* Streaming responses
* PDF and multi-document support
* Persistent conversational memory
* Cloud deployment
* Enhanced safety and evaluation pipeline

---

## Author

Aryansh Sinha

---

## License

This project is open-source and available for modification and use.
