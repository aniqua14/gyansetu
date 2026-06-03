# llm/prompt_template.py

def build_prompt(query: str, context: str) -> str:
    prompt = f"""You are a helpful assistant for Bangladeshi students 
seeking information about scholarships, university admissions, 
research papers, and studying abroad.

Use the context below to answer the question as helpfully as possible.
Extract relevant information even if the context is not perfectly clean.
Ignore formatting artifacts like [edit], [1], [2] in the text.
If the context contains relevant information, use it to answer.
Only say you don't have enough information if the context contains
absolutely nothing related to the question.

For every fact you state, mention which source it came from
using the format: (Source N).

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:"""
    return prompt


def build_bangla_prompt(query: str, context: str) -> str:
    prompt = f"""আপনি বাংলাদেশী শিক্ষার্থীদের জন্য একজন সহায়ক সহকারী।
বৃত্তি, বিশ্ববিদ্যালয় ভর্তি, গবেষণাপত্র এবং বিদেশে পড়াশোনা 
সম্পর্কে তথ্য প্রদান করুন।

নিচের context ব্যবহার করে প্রশ্নের উত্তর বাংলায় দিন।
context এ [edit], [1], [2] এই ধরনের চিহ্ন উপেক্ষা করুন।
context এ যদি প্রাসঙ্গিক তথ্য থাকে তাহলে সেটি ব্যবহার করুন।
শুধুমাত্র তখনই বলুন যথেষ্ট তথ্য নেই যদি context এ সত্যিই
প্রশ্নের সাথে সম্পর্কিত কিছুই না থাকে।

প্রতিটি তথ্যের জন্য শুধুমাত্র (Source 1), (Source 2) এই ফরম্যাটে উৎস উল্লেখ করুন। পুরো URL লিখবেন না।

CONTEXT:
{context}

প্রশ্ন:
{query}

উত্তর:"""
    return prompt
