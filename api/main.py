# api/main.py
from llm.generator import generate_answer
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pathlib import Path
import sys

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


@app.get("/health")
def health():
    """Returns basic system health info."""
    return {
        "status":    "healthy",
        "model":     "llama-3.1-8b-instant",
        "embedding": "all-MiniLM-L6-v2",
        "database":  "ChromaDB"
    }
