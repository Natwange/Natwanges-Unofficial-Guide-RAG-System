"""
Grounded answer generation (Milestone 5, stage 5 of the diagram).

Retrieves the top-k chunks for a question, formats them into a context block,
and asks Groq's llama-3.3-70b-versatile to answer using ONLY that context.
Grounding is enforced two ways:

  1. A strict system prompt that forbids outside knowledge and mandates the
     exact decline phrase when the context is insufficient.
  2. A relevance gate: if no retrieved chunk is close enough (cosine distance
     under RELEVANCE_THRESHOLD), we decline *without* calling the LLM, so an
     out-of-domain question can't be answered from training knowledge.

Source attribution is guaranteed programmatically: the returned `sources` come
from the retrieved chunks' metadata, not from whatever the model chooses to
write.

Usage:
    python -m src.generate "your question"
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

from src.retrieve import retrieve, DEFAULT_K

MODEL = "llama-3.3-70b-versatile"
DECLINE = "I don't have enough information on that."
# Cosine distance above which a chunk is treated as not relevant. Tuned to this
# corpus/model after inspecting real retrieval distances in Milestone 4.
RELEVANCE_THRESHOLD = 0.65

SYSTEM_PROMPT = (
    "You are a careers assistant for international students. Answer the user's "
    "question using ONLY the information in the provided context documents. "
    "Do not use any outside or prior knowledge, and do not guess. "
    f"If the context does not contain enough information to answer, reply with "
    f"exactly this sentence and nothing else: \"{DECLINE}\" "
    "When you use a fact, cite its source id in square brackets, e.g. [source_09]. "
    "Be concise and specific."
)

_client = None


def _get_client():
    """Create the Groq client once, loading GROQ_API_KEY from .env."""
    global _client
    if _client is None:
        from groq import Groq
        load_dotenv()
        key = os.getenv("GROQ_API_KEY")
        if not key or key == "your_key_here":
            raise RuntimeError(
                "GROQ_API_KEY is not set. Copy .env.example to .env and add your key.")
        _client = Groq(api_key=key)
    return _client


def _format_context(hits: list[dict]) -> str:
    """Render retrieved chunks as a numbered, source-labelled context block."""
    blocks = []
    for hit in hits:
        header = f"[{hit['source_id']}] {hit['title']}"
        blocks.append(f"{header}\n{hit['text']}")
    return "\n\n---\n\n".join(blocks)


def _unique_sources(hits: list[dict]) -> list[dict]:
    """De-duplicate retrieved hits down to one entry per source document."""
    seen, sources = set(), []
    for hit in hits:
        if hit["source_id"] in seen:
            continue
        seen.add(hit["source_id"])
        sources.append({"source_id": hit["source_id"],
                        "title": hit["title"], "url": hit["url"]})
    return sources


def ask(question: str, k: int = DEFAULT_K,
        threshold: float = RELEVANCE_THRESHOLD) -> dict:
    """Answer a question from the indexed corpus.

    Returns {"answer", "sources", "hits"} where `sources` is the programmatic
    list of documents the answer drew from (empty when the system declines).
    """
    hits = retrieve(question, k=k)
    relevant = [h for h in hits if h["distance"] <= threshold]

    # Relevance gate: nothing close enough -> decline without calling the LLM.
    if not relevant:
        return {"answer": DECLINE, "sources": [], "hits": hits}

    response = _get_client().chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content":
                f"Context documents:\n\n{_format_context(relevant)}\n\n"
                f"Question: {question}"},
        ],
    )
    answer = response.choices[0].message.content.strip()

    # If the model declined, surface no sources.
    sources = [] if answer.startswith(DECLINE.rstrip(".")) else _unique_sources(relevant)
    return {"answer": answer, "sources": sources, "hits": relevant}


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    question = " ".join(sys.argv[1:]) or "How can I build experience without an internship?"
    result = ask(question)
    print(f"Q: {question}\n")
    print(f"A: {result['answer']}\n")
    print("Sources:")
    for s in result["sources"]:
        print(f"  - {s['source_id']}: {s['title']} ({s['url']})")
    if not result["sources"]:
        print("  (none)")