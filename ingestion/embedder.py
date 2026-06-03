# ingestion/embedder.py
from config import EMBEDDING_MODEL
from sentence_transformers import SentenceTransformer
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Load model once at module level — loading is slow,
# we don't want to reload it on every function call
print(f"Loading embedding model: {EMBEDDING_MODEL}")
model = SentenceTransformer(EMBEDDING_MODEL)
print("Model loaded.")


def embed_chunks(chunks: list[dict]) -> list[list[float]]:
    """
    Takes a list of chunk dicts and returns a list of embedding vectors.
    One vector per chunk, in the same order.
    """
    texts = [chunk["text"] for chunk in chunks]

    # encode() returns a numpy array — we convert to plain Python lists
    # because ChromaDB expects plain lists, not numpy arrays
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    """
    Embeds a single user query string.
    Used at retrieval time — MUST use the same model as embed_chunks().
    """
    embedding = model.encode([query])
    return embedding[0].tolist()
