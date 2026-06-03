# ingestion/loader.py
from config import DATA_RAW, DATA_PROCESSED
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from pathlib import Path
import sys

# Add project root to Python path so 'config' is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def load_pdf(file_path: str) -> dict:
    """
    Reads a PDF file and extracts all text from it.
    Returns a dict with the text and metadata.
    """
    path = Path(file_path)
    reader = PdfReader(str(path))

    full_text = ""
    for page_num, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:                      # some pages are images, skip them
            full_text += page_text + "\n"

    return {
        "text": full_text,
        "source": path.name,              # just the filename e.g. "chevening.pdf"
        "type": "pdf",
        "total_pages": len(reader.pages)
    }


def load_webpage(url: str) -> dict:
    """
    Fetches a webpage and extracts clean readable text.
    Strips all HTML tags, navigation, scripts, and styling.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; BanglaRAG/1.0)"
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()            # throws error if page not found

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove noise — navigation, scripts, styles, footers
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    # Extract clean text
    text = soup.get_text(separator="\n")

    # Remove blank lines and strip whitespace
    lines = [line.strip() for line in text.splitlines()]
    clean_text = "\n".join(line for line in lines if line)

    return {
        "text": clean_text,
        "source": url,
        "type": "webpage"
    }


def load_all_pdfs(folder_path: Path = DATA_RAW) -> list[dict]:
    """
    Loads every PDF found in the data/raw/ folder.
    Returns a list of document dicts.
    """
    documents = []
    pdf_files = list(folder_path.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDFs found in {folder_path}")
        return documents

    for pdf_path in pdf_files:
        print(f"Loading: {pdf_path.name}")
        doc = load_pdf(str(pdf_path))
        documents.append(doc)
        print(f"  → {len(doc['text'])} characters, {doc['total_pages']} pages")

    return documents


# ── Quick test ────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Testing webpage loader ===\n")

    # Wikipedia is reliable and never blocks scrapers
    url = "https://en.wikipedia.org/wiki/Chevening_Scholarship"
    print(f"Fetching: {url}")

    doc = load_webpage(url)
    print(f"Characters extracted: {len(doc['text'])}")
    print(f"Source: {doc['source']}")
    print(f"\nFirst 500 characters:\n")
    print(doc['text'][:500])
