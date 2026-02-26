import json
import google.generativeai as genai
from .vectorstore import get_random_chunks


def generate_study_material(subject):
    chunks = get_random_chunks(subject, k=7)

    if not chunks:
        return {"mcqs": [], "short_questions": []}

    context_parts = []
    for c in chunks:
        context_parts.append(
            f"[page_num: {c.get('page_num', 'Unknown')}, file: {c['file_name']}]\n{c['text']}"
        )
    context = "\n\n".join(context_parts)

    prompt = (
        "You are a strict study assistant. Generate study material STRICTLY AND ONLY from the provided Context.\n"
        "Do NOT invent new facts, use outside knowledge, or make assumptions not explicitly supported by the Context.\n\n"
        "Context:\n" + context + "\n\n"
        "Generate exactly:\n"
        "- 5 MCQs, each with 4 options (A/B/C/D), the correct answer letter, "
        "a short explanation, and the source page_num.\n"
        "- 3 short-answer questions with model answers and the source page_num.\n\n"
        "Return ONLY valid JSON in this exact format (no markdown, no extra text):\n"
        "{\n"
        '  "mcqs": [\n'
        "    {\n"
        '      "question": "...",\n'
        '      "options": {"A": "...", "B": "...", "C": "...", "D": "..."},\n'
        '      "correct": "A",\n'
        '      "explanation": "...",\n'
        '      "page_num": 1\n'
        "    }\n"
        "  ],\n"
        '  "short_questions": [\n'
        "    {\n"
        '      "question": "...",\n'
        '      "answer": "...",\n'
        '      "page_num": 1\n'
        "    }\n"
        "  ]\n"
        "}"
    )

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)

    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"mcqs": [], "short_questions": [], "raw": text}
