# api/main.py
from config import GROQ_MODEL
from llm.generator import generate_answer
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, UploadFile, File
from pathlib import Path
import requests
import sys
from io import BytesIO

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ── App setup ─────────────────────────────────────────────────
app = FastAPI(
    title="GyanSetu API",
    description="RAG powered Research Assistant for Bangladeshi Students — জ্ঞানের সেতু",
    version="1.0.0"
)
# Allow Streamlit frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request and Response models ────────────────────────────────
class QueryRequest(BaseModel):
    query: str
    bangla: bool = None    # None = auto detect


class QueryResponse(BaseModel):
    answer:   str
    sources:  list[str]
    language: str
    num_chunks_retrieved: int


class IngestURLRequest(BaseModel):
    url: str


class IngestURLResponse(BaseModel):
    message: str
    chunks_added: int = 0
    source_type: str = ""


# ── Routes ─────────────────────────────────────────────────────
@app.get("/")
def root():
    """Health check — confirms API is running."""
    return {"status": "BanglaRAG API is running"}


@app.post("/ask", response_model=QueryResponse)
def ask(request: QueryRequest):
    """
    Main RAG endpoint.
    Accepts a question in English or Bangla.
    Returns a grounded cited answer.
    """
    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )

    try:
        result = generate_answer(
            query=request.query,
            bangla=request.bangla
        )
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            language=result["language"],
            num_chunks_retrieved=len(result["chunks"])
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"RAG pipeline error: {str(e)}"
        )


@app.post("/ingest-url", response_model=IngestURLResponse)
def ingest_url(request: IngestURLRequest):
    """
    Ingests a user-submitted URL into the knowledge base.
    Reuses the same scraping, chunking, embedding, and storage
    pipeline as the static corpus.
    """
    from ingestion.loader import load_webpage_dynamic
    from ingestion.chunker import chunk_document
    from ingestion.embedder import embed_chunks
    from vectorstore.store import get_collection, add_chunks

    url = request.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")

    # ── Duplicate check ───────────────────────────────────────
    collection = get_collection()
    try:
        existing = collection.get(where={"source": url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error during duplicate check: {str(e)}")

    if existing and existing["ids"]:
        return IngestURLResponse(
            message=f"'{url}' is already in the knowledge base",
        )

    # ── Step 1: Scrape ────────────────────────────────────────
    try:
        doc = load_webpage_dynamic(url)
    except requests.Timeout:
        raise HTTPException(
            status_code=400,
            detail="Request timed out — could not reach that URL. Try a different URL or check the link."
        )
    except requests.HTTPError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Page returned status {e.response.status_code}. Ensure the URL is accessible."
        )
    except requests.ConnectionError:
        raise HTTPException(
            status_code=400,
            detail="Could not connect to that URL. Check the address and try again."
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to scrape URL: {str(e)}"
        )

    # ── Step 2: Validate extracted text ───────────────────────
    if len(doc["text"]) < 200:
        raise HTTPException(
            status_code=400,
            detail="Extracted text is too short (under 200 characters). "
                   "The page may be JS-rendered, require login, or contain no readable content."
        )

    # ── Step 3: Chunk ─────────────────────────────────────────
    try:
        chunks = chunk_document(doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chunking failed: {str(e)}")

    # ── Step 4: Embed ─────────────────────────────────────────
    try:
        embeddings = embed_chunks(chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")

    # ── Step 5: Store (tagged as dynamic) ─────────────────────
    try:
        add_chunks(collection, chunks, embeddings, source_type="dynamic")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage failed: {str(e)}")

    return IngestURLResponse(
        message=f"Successfully ingested '{url}'",
        chunks_added=len(chunks),
        source_type="dynamic",
    )


# ── PDF text extraction ─────────────────────────────────────────
def extract_pdf_text(file_bytes: bytes) -> str:
    """
    Extract text from a PDF using pdfplumber, with PyMuPDF as fallback.
    Returns empty string if extraction yields <200 characters.
    """
    text = ""

    # Try pdfplumber first — handles multi-column and tables well
    try:
        import pdfplumber
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            pages = []
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    pages.append(t)
            text = "\n".join(pages)
    except Exception:
        text = ""

    if len(text.strip()) >= 200:
        return text.strip()

    # Fallback: PyMuPDF (fitz)
    try:
        import fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages = []
        for page in doc:
            t = page.get_text()
            if t:
                pages.append(t)
        text = "\n".join(pages)
        doc.close()
    except Exception:
        text = ""

    if len(text.strip()) >= 200:
        return text.strip()

    return ""


# ── Ingest PDF ──────────────────────────────────────────────────
@app.post("/ingest-pdf", response_model=IngestURLResponse)
def ingest_pdf(file: UploadFile = File(...)):
    """
    Ingests a user-uploaded PDF into the knowledge base.
    Reuses the same chunking, embedding, and storage pipeline.
    """
    import hashlib
    from ingestion.chunker import chunk_document
    from ingestion.embedder import embed_chunks
    from vectorstore.store import get_collection, add_chunks

    # ── Step 1: Validate file type ──────────────────────────────
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted. Please upload a .pdf file."
        )

    # ── Step 2: Read file content ───────────────────────────────
    try:
        contents = file.file.read()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not read uploaded file: {str(e)}"
        )

    # ── Step 3: Check file size (10MB limit) ────────────────────
    MAX_SIZE = 10 * 1024 * 1024
    if len(contents) > MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File is too large (over 10MB). Please upload a smaller PDF."
        )

    # ── Step 4: Compute content hash for dedup ──────────────────
    file_hash = hashlib.md5(contents).hexdigest()
    filename = file.filename

    # ── Step 5: Duplicate check ─────────────────────────────────
    collection = get_collection()
    try:
        existing = collection.get(where={"file_hash": file_hash})
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error during duplicate check: {str(e)}"
        )

    if existing and existing["ids"]:
        return IngestURLResponse(
            message=f"'{filename}' is already in the knowledge base",
        )

    # ── Step 6: Extract text ────────────────────────────────────
    try:
        text = extract_pdf_text(contents)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to extract text from PDF: {str(e)}"
        )

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Could not extract readable text from this PDF — "
                   "it may be scanned or image-only. Try a text-based PDF."
        )

    # ── Step 7: Build document dict ─────────────────────────────
    doc = {
        "text": text,
        "source": filename,
        "type": "pdf",
    }

    # ── Step 8: Chunk ───────────────────────────────────────────
    try:
        chunks = chunk_document(doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chunking failed: {str(e)}")

    # ── Step 9: Embed ───────────────────────────────────────────
    try:
        embeddings = embed_chunks(chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")

    # ── Step 10: Store (tagged as pdf) ──────────────────────────
    try:
        add_chunks(collection, chunks, embeddings, source_type="pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage failed: {str(e)}")

    # ── Step 11: Attach file_hash to stored metadata ────────────
    try:
        from datetime import datetime, timezone
        ids = [
            hashlib.md5((chunk["source"] + chunk["text"]).encode()).hexdigest()
            for chunk in chunks
        ]
        ingested_at = datetime.now(timezone.utc).isoformat()
        metadatas = [
            {
                "source": chunk["source"],
                "source_url": chunk["source"],
                "type": chunk["type"],
                "chunk_index": chunk["chunk_index"],
                "source_type": "pdf",
                "ingested_at": ingested_at,
                "file_hash": file_hash,
            }
            for chunk in chunks
        ]
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=[chunk["text"] for chunk in chunks],
            metadatas=metadatas,
        )
    except Exception as e:
        # Non-fatal: ingestion succeeded, only file_hash tracking failed
        print(f"[ingest-pdf] Warning: could not store file_hash: {e}")

    return IngestURLResponse(
        message=f"Successfully ingested '{filename}'",
        chunks_added=len(chunks),
        source_type="pdf",
    )


@app.get("/health")
def health():
    """Returns basic system health info."""
    return {
        "status":    "healthy",
        "model":     GROQ_MODEL,
        "embedding": "all-MiniLM-L6-v2",
        "database":  "ChromaDB"
    }
