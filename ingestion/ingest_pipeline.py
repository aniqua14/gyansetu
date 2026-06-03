# ingestion/ingest_pipeline.py
from vectorstore.store import get_collection, add_chunks, get_collection_stats
from ingestion.embedder import embed_chunks
from ingestion.chunker import chunk_documents
from ingestion.loader import load_webpage
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def ingest_urls(urls: list[str]):
    """
    Full ingestion pipeline for a list of URLs:
    1. Load each webpage
    2. Chunk all documents
    3. Embed all chunks
    4. Store in ChromaDB
    """
    print("\n=== Step 1: Loading documents ===")
    documents = []
    for url in urls:
        print(f"Fetching: {url}")
        try:
            doc = load_webpage(url)
            documents.append(doc)
            print(f"  → {len(doc['text'])} characters")
        except Exception as e:
            print(f"  → FAILED: {e}")

    print(f"\nLoaded {len(documents)} documents successfully\n")

    print("=== Step 2: Chunking ===")
    chunks = chunk_documents(documents)
    print(f"\nTotal chunks: {len(chunks)}\n")

    print("=== Step 3: Embedding ===")
    embeddings = embed_chunks(chunks)
    print(f"\nEmbedded {len(embeddings)} chunks\n")

    print("=== Step 4: Storing in ChromaDB ===")
    collection = get_collection()
    add_chunks(collection, chunks, embeddings)

    stats = get_collection_stats(collection)
    print(f"\nDatabase stats: {stats}")
    print("\nIngestion complete!")


# ── Run the pipeline ───────────────────────────────────────────
if __name__ == "__main__":

    # Our starter corpus — reliable Wikipedia pages on each topic
    urls = [
        # Scholarships
        "https://en.wikipedia.org/wiki/Chevening_Scholarship",
        "https://en.wikipedia.org/wiki/Commonwealth_Scholarship",
        "https://en.wikipedia.org/wiki/DAAD",
        "https://en.wikipedia.org/wiki/Fulbright_Program",
        "https://en.wikipedia.org/wiki/Erasmus_Programme",

        # University admissions
        "https://en.wikipedia.org/wiki/University_of_Toronto",
        "https://en.wikipedia.org/wiki/University_of_British_Columbia",
        "https://en.wikipedia.org/wiki/National_University_of_Singapore",
        "https://en.wikipedia.org/wiki/University_of_Melbourne",

        # Research databases
        "https://en.wikipedia.org/wiki/Google_Scholar",
        "https://en.wikipedia.org/wiki/ArXiv",
        "https://en.wikipedia.org/wiki/Semantic_Scholar",

        # Visa and study abroad
        "https://en.wikipedia.org/wiki/Student_visa",
        "https://en.wikipedia.org/wiki/International_student",
    ]

    ingest_urls(urls)
