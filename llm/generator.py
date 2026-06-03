# llm/generator.py
from retrieval.language_detector import is_bangla
from retrieval.retriever import retrieve, format_context
from llm.prompt_template import build_prompt, build_bangla_prompt
from config import GROQ_API_KEY, GROQ_MODEL, MAX_TOKENS
from groq import Groq
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# Initialize Groq client once at module level
client = Groq(api_key=GROQ_API_KEY)


def translate_to_english(query: str) -> str:
    """
    Translates a Bangla query to English using Groq.
    This ensures retrieval always happens in English
    where our embedding model is strong.
    """
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": f"Translate this Bangla text to English. Return only the translation, nothing else:\n\n{query}"
            }
        ],
        max_tokens=200,
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def generate_answer(query: str, bangla: bool = None) -> dict:
    """
    Full RAG pipeline in one function.
    If bangla=None, language is detected automatically.
    If bangla=True, forces Bangla response.
    If bangla=False, forces English response.

    Returns a dict with:
    - answer: the LLM generated text
    - sources: list of unique source URLs cited
    - chunks: the raw retrieved chunks
    - language: detected language ('bn' or 'en')
    """

    # Auto-detect language if not specified
    if bangla is None:
        bangla = is_bangla(query)

    # Step 1 — retrieve relevant chunks
    # For Bangla queries, translate to English first so retrieval works correctly
    retrieval_query = translate_to_english(query) if bangla else query
    print(f"Retrieval query: {retrieval_query}")  # helpful for debugging
    chunks = retrieve(retrieval_query)

    if not chunks:
        no_info = "এই প্রশ্নের উত্তর দেওয়ার মতো যথেষ্ট তথ্য আমার কাছে নেই।" if bangla else "I don't have enough information to answer this question."
        return {"answer": no_info, "sources": [], "chunks": [], "language": "bn" if bangla else "en"}

    # Step 2 — format context
    context = format_context(chunks)

    # Step 3 — build prompt based on language
    if bangla:
        prompt = build_bangla_prompt(query, context)
    else:
        prompt = build_prompt(query, context)

    # Step 4 — call Groq API
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=MAX_TOKENS,
        temperature=0.2,
    )

    # Step 5 — extract answer and sources
    answer = response.choices[0].message.content
    sources = list(dict.fromkeys(chunk["source"] for chunk in chunks))
    language = "bn" if bangla else "en"

    return {
        "answer":   answer,
        "sources":  sources,
        "chunks":   chunks,
        "language": language
    }


# ── Quick test ─────────────────────────────────────────────────
if __name__ == "__main__":

    test_queries = [
        # English queries
        "What are the eligibility requirements for Chevening scholarship?",

        # Bangla queries
        "শেভেনিং বৃত্তির যোগ্যতার শর্তগুলো কি?",
        "কানাডায় পড়াশোনার জন্য কিভাবে ভিসা পাবো?",
        "গুগল স্কলার কিভাবে গবেষণাপত্র খুঁজে পেতে সাহায্য করে?",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"QUESTION: {query}")
        print(f"{'='*60}")

        result = generate_answer(query)

        print(f"Language detected: {result['language']}")
        print(f"\nANSWER:\n{result['answer']}")
        print(f"\nSOURCES:")
        for source in result['sources']:
            print(f"  - {source}")
