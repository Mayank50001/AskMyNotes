import pdfplumber
import google.generativeai as genai
from .embeddings import embed_text
from .vectorstore import search_index

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 250


def process_pdf(file_path, file_name, subject_name):
    pages = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                pages.append({"page_num": i + 1, "text": page_text + "\n"})

    chunks = []
    for page in pages:
        text = page["text"]
        start = 0
        while start < len(text):
            end = start + CHUNK_SIZE
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "subject": subject_name,
                    "file_name": file_name,
                    "page_num": page["page_num"],
                    "text": chunk_text,
                })
            start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def ask_question(subject, question, history=""):
    query_embedding = embed_text(question)
    scores, results = search_index(subject, query_embedding, top_k=3)

    if not scores or scores[0] < 0.65:
        return {
            "answer": f"Not found in your notes for {subject}",
            "confidence": "Low",
            "citations": [],
        }

    context = "\n\n".join([r["text"] for r in results])

    prompt = (
        f"You are a strict study assistant. You must answer the Question ONLY using the exact information provided in the Context below.\n"
        f"Do NOT use your own knowledge or outside information under any circumstances for the main answer.\n"
        f"If the answer is not explicitly present in the Context, or if the Question asks for something entirely unrelated to the context, reply exactly: "
        f"'Not found in your notes for {subject}'\n\n"
        f"But if the question asks for elaboration on a topic already in context, you may use your knowledge to provide insight under an 'LLM Insights' section.\n\n"
        f"Previous Conversation History (Use this ONLY to understand the context of the user's new question, do not pull facts from it if not in Context):\n{history}\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{question}"
    )

    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    response = model.generate_content(prompt)

    # Strict citation overriding
    if "Not found in your notes for" in response.text:
        confidence = "Low"
        citations = []
    else:
        confidence = "High" if scores[0] >= 0.8 else "Medium"
        citations = []
        for r in results:
            citations.append({
                "file": r["file_name"],
                "page_num": r.get("page_num", "Unknown"),
                "snippet": r["text"][:200],
            })

    return {
        "answer": response.text,
        "confidence": confidence,
        "citations": citations,
    }
