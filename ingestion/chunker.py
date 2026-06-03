# ingestion/chunker.py
from ingestion.loader import load_webpage
from config import CHUNK_SIZE, CHUNK_OVERLAP
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def chunk_document(document: dict) -> list[dict]:
    """
    Takes a document dict (from loader.py) and splits its text
    into overlapping chunks. Returns a list of chunk dicts,
    each with the text and metadata attached.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    chunks = splitter.split_text(document["text"])

    # Attach metadata to every chunk so we know where it came from
    chunk_dicts = []
    for i, chunk_text in enumerate(chunks):
        chunk_dicts.append({
            "text": chunk_text,
            "source": document["source"],
            "type": document["type"],
            "chunk_index": i,         # position of this chunk in the document
            "total_chunks": len(chunks)
        })

    return chunk_dicts


def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    Chunks a list of documents. Just calls chunk_document()
    on each one and combines the results.
    """
    all_chunks = []
    for doc in documents:
        chunks = chunk_document(doc)
        all_chunks.extend(chunks)
        print(f"  '{doc['source']}' → {len(chunks)} chunks")
    return all_chunks


# ── Quick test ────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Testing chunker ===\n")

    # Load the same Wikipedia page we tested with
    url = "https://en.wikipedia.org/wiki/Chevening_Scholarship"
    print(f"Loading: {url}")
    doc = load_webpage(url)
    print(f"Raw text length: {len(doc['text'])} characters\n")

    # Chunk it
    print("Chunking...\n")
    chunks = chunk_document(doc)

    print(f"Total chunks produced: {len(chunks)}")
    print(f"Chunk size setting: {CHUNK_SIZE} chars")
    print(f"Overlap setting: {CHUNK_OVERLAP} chars")

    print(f"\n--- Chunk 0 ---")
    print(chunks[0]['text'])
    print(f"\n--- Chunk 1 ---")
    print(chunks[1]['text'])
    print(f"\n--- Last chunk ---")
    print(chunks[-1]['text'])

    print(f"\n--- Metadata of chunk 0 ---")
    for key, value in chunks[0].items():
        if key != "text":
            print(f"  {key}: {value}")
