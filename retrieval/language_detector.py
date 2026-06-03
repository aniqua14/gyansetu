# retrieval/language_detector.py
from langdetect import detect, LangDetectException


def detect_language(text: str) -> str:
    """
    Detects the language of the input text.
    Returns 'bn' for Bangla, 'en' for English,
    or 'en' as default if detection fails.
    """
    try:
        lang = detect(text)
        return lang
    except LangDetectException:
        # If detection fails (very short text etc), default to English
        return "en"


def is_bangla(text: str) -> bool:
    """
    Returns True if the text is detected as Bangla.
    This is what generator.py will call to decide
    which prompt template to use.
    """
    return detect_language(text) == "bn"


# ── Quick test ─────────────────────────────────────────────────
if __name__ == "__main__":

    test_texts = [
        "What are the eligibility requirements for Chevening scholarship?",
        "শেভেনিং বৃত্তির যোগ্যতার শর্তগুলো কি?",
        "How do I apply for a Canadian student visa?",
        "কানাডায় পড়াশোনার জন্য কিভাবে ভিসা পাবো?",
        "University of Toronto acceptance rate",
        "ঢাকা বিশ্ববিদ্যালয়ে ভর্তি হতে কি লাগে?",
    ]

    print("=== Language Detection Test ===\n")
    for text in test_texts:
        lang = detect_language(text)
        bangla = is_bangla(text)
        print(f"Text: {text[:50]}")
        print(f"  Detected: {lang} | Is Bangla: {bangla}\n")
