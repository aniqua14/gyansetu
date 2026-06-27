# Gyanshetu — System Flowchart

```mermaid
flowchart TD
    %% ─── INGESTION PIPELINE ───
    subgraph Ingestion["📥 Ingestion Pipeline"]
        direction TB
        A1["📄 Source Documents<br/>(PDFs or Web URLs)"]:::ingest
        A2["🗂️ Document Loader<br/>(`ingestion/loader.py`)<br/>pypdf · BeautifulSoup"]:::ingest
        A3["✂️ Text Chunker<br/>(`ingestion/chunker.py`)<br/>RecursiveCharacterTextSplitter<br/>chunk_size=500 · overlap=50"]:::ingest
        A4["🧠 Embedding Model<br/>(`ingestion/embedder.py`)<br/>all-MiniLM-L6-v2<br/>→ 384-dim vectors"]:::ingest
        A5["🗄️ Vector Store<br/>(`vectorstore/store.py`)<br/>ChromaDB · cosine similarity<br/>MD5 dedup via upsert()"]:::ingest

        A1 -->|"load_pdf() / load_webpage()"| A2
        A2 -->|"dict: {text, source, type}"| A3
        A3 -->|"list[dict]: {text, source, chunk_index}"| A4
        A4 -->|"list[list[float]]: 384-dim embeddings"| A5
    end

    %% ─── QUERY PIPELINE ───
    subgraph Query["💬 Query / RAG Pipeline"]
        direction TB
        B1["👤 User Input<br/>(Streamlit UI or FastAPI POST)"]:::query
        B2["🔍 Language Detector<br/>(`retrieval/language_detector.py`)<br/>langdetect → en / bn"]:::query
        B3["🌐 Query Translator<br/>(`llm/generator.py:translate_to_english()`)<br/>Groq · Llama 3.1 8B · temp=0<br/>Bangla → English"]:::query
        B4["🔎 Retriever<br/>(`retrieval/retriever.py`)<br/>embed_query() → ChromaDB query<br/>top_k=4 · similarity > 0.5<br/>format_context()"]:::query
        B5A["📝 English Prompt<br/>(`llm/prompt_template.py:build_prompt()`)"]:::query
        B5B["📝 বাংলা Prompt<br/>(`llm/prompt_template.py:build_bangla_prompt()`)"]:::query
        B6["🤖 LLM Generator<br/>(`llm/generator.py:generate_answer()`)<br/>Groq · Llama 3.1 8B Instant<br/>temp=0.2 · max_tokens=1024"]:::query
        B7["✅ Response Assembly<br/>{answer, sources, chunks, language}"]:::query
        B8["📤 Final Response<br/>(Streamlit chat · FastAPI JSON)"]:::query

        B1 --> B2
        B2 -->|"bn"| B3
        B2 -->|"en"| B4
        B3 --> B4
        B4 --> A5
        A5 -->|"top-4 relevant chunks"| B4
        B4 -->|"context string"| B5A
        B4 -->|"context string"| B5B
        B5A --> B6
        B5B --> B6
        B6 --> B7
        B7 --> B8
    end

    %% ─── STYLING ───
    classDef ingest fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#01579b
    classDef query fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100
```

## Pipeline Overview

| Step | Component | Technology |
|------|-----------|------------|
| **Load** | `ingestion/loader.py` | pypdf, BeautifulSoup, requests |
| **Chunk** | `ingestion/chunker.py` | LangChain RecursiveCharacterTextSplitter (500/50) |
| **Embed** | `ingestion/embedder.py` | sentence-transformers all-MiniLM-L6-v2 |
| **Store** | `vectorstore/store.py` | ChromaDB PersistentClient, cosine similarity, MD5 dedup |
| **Detect** | `retrieval/language_detector.py` | langdetect |
| **Translate** | `llm/generator.py` | Groq — llama-3.1-8b-instant, temp=0 |
| **Retrieve** | `retrieval/retriever.py` | Embed query → ChromaDB similarity search → filter > 0.5 |
| **Generate** | `llm/generator.py` | Groq — llama-3.1-8b-instant, temp=0.2, max_tokens=1024 |
| **API** | `api/main.py` | FastAPI, CORS, Pydantic models |
| **UI** | `frontend/app.py` | Streamlit chat with source links |
