---
title: GyanSetu
emoji: 🎓
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
app_file: frontend/app.py
pinned: false
---

# GyanSetu — জ্ঞানের সেতু 🎓
### RAG-Powered, Bilingual Research Assistant for Bangladeshi Students

GyanSetu helps Bangladeshi students find accurate, cited information about scholarships, university admissions, research, and studying abroad — in English or Bangla. Every answer is grounded in retrieved source documents, not model memory, and includes citations back to the original source.

---
## 🚀 Live Demo

👉 **[Try GyanSetu on Hugging Face Spaces](https://huggingface.co/spaces/aniqua-nawar/gyansetu)**

---
## Key Features

- **Bilingual by design** — ask questions in English or Bangla; the system detects language automatically and answers in the same language it was asked
- **Dynamic knowledge base** — users can expand the knowledge base live via URL ingestion or direct PDF upload, not just a fixed pre-built corpus
- **Grounded, cited answers** — every response links back to the specific source(s) it was generated from, with a similarity threshold that filters out weak/irrelevant retrieval matches before generation
- **RAG architecture** — retrieval-augmented generation avoids LLM hallucination by grounding answers in real, retrieved documents

---
## What is RAG?
Large Language Models (LLMs) hallucinate — they generate confident but false answers when asked about specific facts. RAG (Retrieval-Augmented Generation) solves this by retrieving real documents first, then grounding the LLM's answer in that evidence, with citations back to the source.

---
## Architecture

```
User Question (English or Bangla)
        ↓
Language Detection (langdetect)
        ↓
[If Bangla] Translate to English (Groq)
        ↓
Query Embedding (all-MiniLM-L6-v2)
        ↓
Vector Similarity Search (ChromaDB) + Similarity Threshold Filter
        ↓
Top-K Relevant Chunks Retrieved (or empty → graceful fallback)
        ↓
Prompt Engineering (context + question)
        ↓
LLM Generation (Groq — openai/gpt-oss-120b)
        ↓
Grounded Answer with Citations
(in the user's original language)
```

**Dynamic Ingestion Pipeline:**
```
User submits URL or uploads PDF
        ↓
Content extraction and cleaning
        ↓
Chunking (RecursiveCharacterTextSplitter)
        ↓
Embedding (all-MiniLM-L6-v2)
        ↓
Stored in ChromaDB (available for retrieval immediately)
```

---
## Project Structure

```
gyansetu/
    ├── ingestion/
    │   ├── loader.py             # PDF and webpage loader
    │   ├── chunker.py            # splits documents into passages
    │   ├── embedder.py           # HuggingFace embedding model
    │   └── ingest_pipeline.py    # runs full ingestion
    ├── vectorstore/
    │   ├── store.py              # ChromaDB wrapper
    │   └── chroma_db/            # persistent vector store (tracked via Git LFS)
    ├── retrieval/
    │   ├── retriever.py          # query → top-k chunks, similarity-filtered
    │   └── language_detector.py  # English vs Bangla detection
    ├── llm/
    │   ├── prompt_template.py    # prompt engineering
    │   └── generator.py          # Groq API + full RAG pipeline
    ├── api/
    │   └── main.py               # FastAPI backend (incl. dynamic ingestion endpoints)
    ├── frontend/
    │   └── app.py                # Streamlit UI
    ├── config.py                 # all settings in one place
    ├── requirements.txt
    └── .env                      # API keys (never commit this)
```

---
## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Embeddings | HuggingFace all-MiniLM-L6-v2 | Free, runs locally |
| Vector DB | ChromaDB | Free, persistent, local |
| LLM | Groq — openai/gpt-oss-120b | Fast inference, strong multilingual (incl. Bangla) support |
| Backend | FastAPI | Industry-standard API framework |
| Frontend | Streamlit | Rapid ML app development |
| Language Detection | langdetect | Automatic English/Bangla routing |
| Deployment | Docker on Hugging Face Spaces | Free hosting, live public demo |

---
## Document Corpus

Base corpus covers scholarships (Chevening, Commonwealth, Fulbright, Erasmus, DAAD), universities (Toronto, UBC, NUS, Melbourne), research databases (Google Scholar, arXiv, Semantic Scholar), and visa/international study topics — plus anything users add live via URL or PDF upload.

---
## Setup and Installation

```bash
# Clone the repo
git clone https://github.com/aniqua14/gyansetu.git
cd gyansetu

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash

# Install dependencies
pip install -r requirements.txt

# Add your API key
# Create a .env file in the project root and add:
# GROQ_API_KEY=your_groq_api_key_here
# Get your free key at: https://console.groq.com

# Run ingestion (builds the base vector database)
python ingestion/ingest_pipeline.py

# Start the backend
venv/Scripts/uvicorn.exe api.main:app --reload

# Start the frontend (in a separate terminal)
PYTHONPATH=. streamlit run frontend/app.py
```

---
## Deployment

This project pushes to two separate git remotes:
- **`origin`** (GitHub) — source code, tracked on the `dynamic-ingestion` branch
- **`space`** (Hugging Face) — the live demo, which always runs from its `main` branch

To update the live demo after making changes:
```bash
git push space dynamic-ingestion:main
```
The vector store (`vectorstore/chroma_db/`) is tracked via **Git LFS**, since Hugging Face Spaces requires LFS for binary files.

---
## Example Queries

**English:**
> "What are the eligibility requirements for the Chevening scholarship?"

**Bangla:**
> "ফুলব্রাইট বৃত্তি কি?"

---
## Known Limitations

- Bangla queries are answered via automatic translation — the query is translated to English for retrieval, then the answer is generated in Bangla
- Very short Bangla queries (1–2 words) may not detect correctly — use full sentences for best results
- Wikipedia-sourced content may occasionally contain formatting noise (e.g. `[edit]`, `[1]`)

---
## Author

Built by Aniqua Nawar — CS Graduate, Bangladesh
- 🤗 [Hugging Face](https://huggingface.co/aniqua-nawar)
- 💻 [GitHub](https://github.com/aniqua14)

---
## License
MIT
