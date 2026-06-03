# vectorstore/store.py
from config import CHROMA_DIR, COLLECTION_NAME
import chromadb
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def get_collection():
    """
    Creates or opens the ChromaDB collection on disk.
    If the collection already exists, it just opens it.
    If it doesn't exist yet, it creates it fresh.
    """
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}  # use cosine similarity
    )
    return collection


def add_chunks(collection, chunks: list[dict], embeddings: list[list[float]]):
    """
    Stores chunks and their embeddings into ChromaDB.
    Uses a hash of the text as ID to prevent duplicates —
    if the same chunk is ingested twice, it just overwrites.
    """
    import hashlib

    ids = [
        hashlib.md5(
            (chunk["source"] + chunk["text"]).encode()
        ).hexdigest()
        for chunk in chunks
    ]

    documents = [chunk["text"] for chunk in chunks]
    metadatas = [
        {
            "source":      chunk["source"],
            "type":        chunk["type"],
            "chunk_index": chunk["chunk_index"],
        }
        for chunk in chunks
    ]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )
    print(f"Stored {len(chunks)} chunks in ChromaDB")


def get_collection_stats(collection) -> dict:
    """
    Returns basic info about what's stored in the collection.
    Useful for debugging and verifying ingestion worked.
    """
    return {
        "collection_name": collection.name,
        "total_chunks":    collection.count(),
    }
