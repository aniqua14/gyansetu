# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_RAW = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"
CHROMA_DIR = BASE_DIR / "vectorstore" / "chroma_db"

# ── Embedding model ────────────────────────────────────────────
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# WARNING: never change this after ingestion without re-ingesting
# all documents. Ingestion and retrieval MUST use the same model.

# ── Chunking ───────────────────────────────────────────────────
CHUNK_SIZE = 500   # characters per chunk
CHUNK_OVERLAP = 50    # overlap between adjacent chunks

# ── Retrieval ──────────────────────────────────────────────────
TOP_K = 4             # number of chunks to retrieve per query

# ── ChromaDB ──────────────────────────────────────────────────
COLLECTION_NAME = "gyansetu_docs"

# ── LLM (Groq) ────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-8b-instant"
MAX_TOKENS = 1024
