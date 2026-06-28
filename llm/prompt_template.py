def build_prompt(query: str, context: str) -> str:
    prompt = f"""You are a helpful research assistant.

Use the context below to answer the question as helpfully and accurately as possible.
Extract relevant information even if the context is not perfectly clean.
Ignore formatting artifacts like [edit], [1], [2] in the text.
If the context contains relevant information, use it to answer — regardless of the topic.
Only say you don't have enough information if the context contains
absolutely nothing related to the question.

IMPORTANT: Carefully read ALL sources below before answering — the most relevant
information is not always in Source 1. Check every source thoroughly before
concluding the answer isn't there.

For every fact you state, mention which source it came from
using the format: (Source N).

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:"""
    return prompt

def build_bangla_prompt(query: str, context: str) -> str:
    prompt = f"""আপনি একজন সহায়ক গবেষণা সহকারী।

নিচের context ব্যবহার করে প্রশ্নের উত্তর বাংলায় দিন।
context এ [edit], [1], [2] এই ধরনের চিহ্ন উপেক্ষা করুন।
context এ যদি প্রাসঙ্গিক তথ্য থাকে তাহলে সেটি ব্যবহার করুন — বিষয় যাই হোক না কেন।
শুধুমাত্র তখনই বলুন যথেষ্ট তথ্য নেই যদি context এ সত্যিই
প্রশ্নের সাথে সম্পর্কিত কিছুই না থাকে।

গুরুত্বপূর্ণ: উত্তর দেওয়ার আগে নিচের সব source ভালোভাবে পড়ুন — সবচেয়ে গুরুত্বপূর্ণ
তথ্য সবসময় Source 1 এ থাকে না। উপসংহারে যাওয়ার আগে প্রতিটি source ভালোভাবে যাচাই করুন।

প্রতিটি তথ্যের জন্য শুধুমাত্র (Source 1), (Source 2) এই ফরম্যাটে উৎস উল্লেখ করুন। পুরো URL লিখবেন না।

CONTEXT:
{context}

প্রশ্ন:
{query}

উত্তর:"""
    return prompt