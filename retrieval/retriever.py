# retrieval/retriever.py
from config import TOP_K
from vectorstore.store import get_collection
from ingestion.embedder import embed_query
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    """
    Takes a user question and returns the top_k most relevant chunks.

    Steps:
    1. Embed the query into a vector (same model used during ingestion)
    2. Ask ChromaDB to find the nearest vectors using cosine similarity
    3. Return the chunks with their text, source, and similarity score
    """

    # Step 1 — embed the query
    query_vector = embed_query(query)

    # Step 2 — search ChromaDB
    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    # Step 3 — format results into clean dicts
    chunks = []
    documents = results["documents"][0]   # list of chunk texts
    metadatas = results["metadatas"][0]   # list of metadata dicts
    # list of distances (lower = more similar)
    distances = results["distances"][0]

    for text, metadata, distance in zip(documents, metadatas, distances):
        similarity = 1 - distance

        if similarity < 0.5:      # chunk is not relevant enough, skip it
            continue

        chunks.append({
            "text":        text,
            "source":      metadata["source"],
            "type":        metadata["type"],
            "chunk_index": metadata["chunk_index"],
            "similarity":  round(similarity, 4)
        })

    return chunks


def format_context(chunks: list[dict]) -> str:
    """
    Formats retrieved chunks into a single context string
    that will be injected into the LLM prompt in Phase 6.

    Each chunk is labeled with its source so the LLM
    can cite it in the answer.
    """
    context_parts = []

    for i, chunk in enumerate(chunks):
        context_parts.append(
            f"[Source {i+1}: {chunk['source']}]\n{chunk['text']}"
        )

    return "\n\n---\n\n".join(context_parts)


# ── Quick test ─────────────────────────────────────────────────
if __name__ == "__main__":

    test_queries = [
        "What are the eligibility requirements for Chevening scholarship?",
        "What is the acceptance rate at University of Toronto?",
        "How do I find research papers using Google Scholar?",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"QUERY: {query}")
        print(f"{'='*60}")

        chunks = retrieve(query)

        for i, chunk in enumerate(chunks):
            print(
                f"\n--- Result {i+1} (similarity: {chunk['similarity']}) ---")
            print(f"Source: {chunk['source']}")
            print(f"Text preview: {chunk['text'][:200]}...")

        print(f"\n--- Formatted context for LLM ---")
        print(format_context(chunks)[:500])
        print("...")
