import time
import google.generativeai as genai
from django.conf import settings

_configured = False

EMBED_MODEL = "gemini-embedding-001"
MAX_RETRIES = 3


def _ensure_configured():
    global _configured
    if not _configured:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _configured = True


def _embed_with_retry(content, task_type):
    _ensure_configured()
    for attempt in range(MAX_RETRIES):
        try:
            result = genai.embed_content(
                model=EMBED_MODEL,
                content=content,
                task_type=task_type,
            )
            return result['embedding']
        except Exception as e:
            if "429" in str(e) and attempt < MAX_RETRIES - 1:
                wait = 20 * (attempt + 1)
                time.sleep(wait)
            else:
                raise


def embed_text(text):
    return _embed_with_retry(text, "retrieval_query")


def embed_texts(texts):
    return _embed_with_retry(texts, "retrieval_document")
