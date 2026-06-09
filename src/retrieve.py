"""
Retrieval over the ChromaDB index (Milestone 4, stage 4 of the diagram).

Embeds a query (with BGE's query prefix) and returns the top-k most similar
chunks together with their cosine distance and source metadata. Lower distance
= more similar; for this corpus, relevant top hits land below ~0.5.

Test it from the project root:
    python -m src.retrieve                      # runs the built-in eval queries
    python -m src.retrieve "your question"      # ad-hoc query
"""

from __future__ import annotations

import sys

from src.store import embed_query, get_collection

DEFAULT_K = 4

# Three of the five planning.md evaluation questions, used as a smoke test.
EVAL_QUERIES = [
    "What advice did a Squarespace recruiter give students without prior SWE "
    "internships applying for new grad roles?",
    "What resume formula was recommended for writing project bullet points?",
    "What are common reasons international students are rejected from internships?",
]


def retrieve(query: str, k: int = DEFAULT_K) -> list[dict]:
    """Return the top-k chunks for a query as dicts with distance + metadata."""
    collection = get_collection()
    result = collection.query(
        query_embeddings=[embed_query(query)],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    hits = []
    for i in range(len(result["ids"][0])):
        meta = result["metadatas"][0][i]
        hits.append({
            "chunk_id": result["ids"][0][i],
            "distance": result["distances"][0][i],
            "text": result["documents"][0][i],
            "source_id": meta.get("source_id"),
            "title": meta.get("title"),
            "url": meta.get("url"),
            "chunk_index": meta.get("chunk_index"),
        })
    return hits


def _print_hits(query: str, k: int = DEFAULT_K) -> None:
    print(f"\n=== QUERY: {query}")
    for rank, hit in enumerate(retrieve(query, k), start=1):
        print(f"\n  #{rank}  distance={hit['distance']:.3f}  "
              f"[{hit['source_id']} / chunk {hit['chunk_index']}] {hit['title']}")
        snippet = hit["text"][:280].strip().replace("\n", " ")
        print(f"      {snippet}...")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    if len(sys.argv) > 1:
        _print_hits(" ".join(sys.argv[1:]))
    else:
        for q in EVAL_QUERIES:
            _print_hits(q)