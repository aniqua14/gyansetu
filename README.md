---
title: GyanSetu
emoji: 🎓
colorFrom: green
colorTo: blue
sdk: docker
app_file: frontend/app.py
pinned: false
---

# GyanSetu — জ্ঞানের সেতু 🎓
### RAG Powered Research Assistant for Bangladeshi Students

GyanSetu helps Bangladeshi students find accurate, cited information
about scholarships, university admissions, research papers, and 
studying abroad — in English or Bangla.

---

## What is RAG?
Large Language Models (LLMs) hallucinate — they generate confident 
but false answers when asked about specific facts. RAG (Retrieval 
Augmented Generation) solves this by retrieving real documents first, 
then grounding the LLM's answer in that evidence.

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
Vector Similarity Search (ChromaDB)
        ↓
Top-K Relevant Chunks Retrieved
        ↓
Prompt Engineering (context + question)
        ↓
LLM Generation (Groq — Llama 3.1)
        ↓
Grounded Answer with Citations
(in the user's original language)
```

---

## Project Structure

```
gyansetu/
    ├── data/
    │   ├── raw/                  # original PDFs and web pages
    │   └── processed/            # cleaned text files
    ├── ingestion/
    │   ├── loader.py             # PDF and webpage loader
    │   ├── chunker.py            # splits documents into passages
    │   ├── embedder.py           # HuggingFace embedding model
    │   └── ingest_pipeline.py    # runs full ingestion
    ├── vectorstore/
    │   ├── store.py              # ChromaDB wrapper
    │   └── chroma_db/            # auto-generated on first run
    ├── retrieval/
    │   ├── retriever.py          # query → top-k chunks
    │   └── language_detector.py  # English vs Bangla detection
    ├── llm/
    │   ├── prompt_template.py    # prompt engineering
    │   └── generator.py          # Groq API + full RAG pipeline
    ├── api/
    │   └── main.py               # FastAPI backend
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
| LLM | Groq — Llama 3.1 8B | Free tier, fast inference |
| Backend | FastAPI | Industry standard API framework |
| Frontend | Streamlit | Rapid ML app development |
| Language Detection | langdetect | Automatic English/Bangla routing |

---

## Document Corpus

### 🏆 Scholarships
| Scholarship | Country | Coverage |
|-------------|---------|----------|
| Chevening Scholarship | UK | Eligibility, selection criteria, history |
| Commonwealth Scholarship | UK/Commonwealth | Eligibility, funding, application |
| Fulbright Program | USA | Grants, degree programs, eligibility |
| Erasmus Programme | Europe | History, funding, student exchange |
| DAAD | Germany | Overview |

### 🎓 Universities
| University | Country | Coverage |
|------------|---------|----------|
| University of Toronto | Canada | Admissions, enrollment, programs |
| University of British Columbia | Canada | Acceptance rate, admissions, programs |
| National University of Singapore | Singapore | Rankings, admissions, programs |
| University of Melbourne | Australia | Admissions, programs, research |

### 🔬 Research Databases
| Platform | Coverage |
|----------|----------|
| Google Scholar | Features, usage, tips |
| arXiv | Preprints, subjects, usage |
| Semantic Scholar | AI-powered search, features |

### ✈️ Visa & International Study
| Topic | Coverage |
|-------|----------|
| Student Visa | Types, requirements, process |
| International Student | Statistics, challenges, support |

> **Note:** Corpus is Wikipedia-based. Official PDF sources will 
> be added in future versions for more accurate answers.

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

# Run ingestion (builds the vector database)
python ingestion/ingest_pipeline.py

# Start the frontend
streamlit run frontend/app.py
```

---

## Example Queries

**English:**
> "What are the eligibility requirements for Chevening scholarship?"

> "How does the Fulbright scholarship work?"

**Bangla:**
> "ফুলব্রাইট বৃত্তি কি?"

> "শেভেনিং বৃত্তির যোগ্যতার শর্তগুলো কি?"

---

## Known Limitations

- Bangla queries are supported via automatic translation —
  the query is translated to English for retrieval,
  then answered in Bangla
- Very short Bangla queries (1-2 words) may not detect
  correctly — use full sentences for best results
- Corpus is currently Wikipedia-based — answers may contain
  Wikipedia formatting noise like [edit] or [1]

---

## Author

Built by Aniqua Nawar — CS Graduate, Bangladesh
Previous project: BanglaMind (Bangla LLM fine-tuning)

---

## License
MIT