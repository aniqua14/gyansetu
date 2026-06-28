# llm/generator.py
from retrieval.language_detector import is_bangla
from retrieval.retriever import retrieve, format_context
from llm.prompt_template import build_prompt, build_bangla_prompt
from config import GROQ_API_KEY, GROQ_MODEL, MAX_TOKENS
from groq import Groq
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# Initialize Groq client once at module level
client = Groq(api_key=GROQ_API_KEY)

# ── Bangla validation ───────────────────────────────────────────
BANGLA_RE = re.compile(r'[\u0980-\u09FF]')


def contains_bangla(text: str) -> bool:
    """Returns True if text contains any Bengali-script Unicode character."""
    return bool(BANGLA_RE.search(text))


class TranslationError(Exception):
    """Raised when Bangla-to-English translation fails after retry."""
    pass


def translate_to_english(query: str) -> str:
    """
    Translates a Bangla query to English using Groq.
    Validates the output: if Bangla characters remain, retries once
    with a stricter few-shot prompt. If translation still fails,
    raises TranslationError instead of silently returning bad input.
    """

    # ── Attempt 1: simple instruction prompt ─────────────────────
    prompt_simple = (
        "Translate this Bangla text to English. "
        "Return only the translation, nothing else:\n\n"
        f"{query}"
    )

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt_simple}],
            max_tokens=200,
            temperature=0,
        )
        translated = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Translation] API error on attempt 1: {e}")
        translated = None

    if translated is not None and not contains_bangla(translated):
        print(f"[Translation] OK: '{query}' → '{translated}'")
        return translated

    # ── Attempt 2: few-shot retry ────────────────────────────────
    print(f"[Translation] Attempt 1 failed. Retrying with few-shot prompt.")
    print(f"[Translation] Original: '{query}'")
    if translated is not None:
        print(f"[Translation] Bad output from attempt 1: '{translated}'")

    prompt_fewshot = (
        "You are a translator. Translate the following Bangla text to English.\n"
        "Return ONLY the English translation. Do not include any explanation,\n"
        "notes, or the original text.\n\n"
        "Example:\n"
        "Bangla: শেভেনিং বৃত্তির যোগ্যতার শর্তগুলো কি?\n"
        "English: What are the eligibility requirements for Chevening scholarship?\n\n"
        "Now translate:\n"
        f"Bangla: {query}\n"
        "English:"
    )

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt_fewshot}],
            max_tokens=200,
            temperature=0,
        )
        translated = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Translation] API error on retry: {e}")
        raise TranslationError(
            f"Translation failed: API error on retry — {e}"
        )

    if translated is not None and not contains_bangla(translated):
        print(f"[Translation] OK (retry): '{query}' → '{translated}'")
        return translated

    print(f"[Translation] Retry also produced Bangla output: '{translated}'")
    raise TranslationError(
        "Translation failed: Groq could not produce an English translation "
        "after two attempts."
    )


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
    if bangla:
        try:
            retrieval_query = translate_to_english(query)
        except TranslationError:
            return {
                "answer": "দুঃখিত, আপনার প্রশ্নটি ইংরেজিতে অনুবাদ করতে ব্যর্থ হয়েছে। "
                          "অনুগ্রহ করে ইংরেজিতে প্রশ্নটি আবার লিখুন।",
                "sources": [],
                "chunks": [],
                "language": "bn"
            }
    else:
        retrieval_query = query
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
