"""
Embed chunks and load them into ChromaDB (Milestone 4, stage 3 of the diagram).

Reads the chunks produced by src/ingest.py (data/processed/chunks.jsonl),
embeds them with bge-small-en-v1.5, and stores each one in ChromaDB together
with its source metadata (source_id, title, url, type, chunk_index, n_chunks)
so answers can later be attributed to the right document.

Run it from the project root:
    python -m src.embed
"""

from __future__ import annotations

import json
import sys

from src.store import (
    CHUNKS_PATH, CHROMA_PATH, COLLECTION_NAME, MODEL_NAME,
    embed_passages, get_client, get_collection,
)

# ChromaDB metadata values must be str / int / float / bool.
METADATA_FIELDS = ("source_id", "title", "url", "type", "chunk_index", "n_chunks")


def load_chunks(path=CHUNKS_PATH) -> list[dict]:
    """Load chunk records written by the ingestion pipeline."""
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run `python -m src.ingest` first.")
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def build_index(batch_size: int = 64) -> int:
    """Embed every chunk and (re)load the ChromaDB collection from scratch.

    The collection is deleted and recreated so re-running after a re-chunk
    never leaves stale or duplicate vectors behind.
    """
    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks from "
          f"{CHUNKS_PATH.relative_to(CHUNKS_PATH.parents[2])}")

    client = get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass  # nothing to delete on a first run
    collection = get_collection()

    print(f"Embedding with {MODEL_NAME} and adding to ChromaDB ...")
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start + batch_size]
        collection.add(
            ids=[c["chunk_id"] for c in batch],
            embeddings=embed_passages([c["text"] for c in batch]),
            documents=[c["text"] for c in batch],
            metadatas=[{k: c[k] for k in METADATA_FIELDS} for c in batch],
        )
        print(f"  added {min(start + batch_size, len(chunks))}/{len(chunks)}")

    total = collection.count()
    print(f"\nDone. Collection '{COLLECTION_NAME}' now holds {total} vectors.")
    print(f"Stored at {CHROMA_PATH}")
    return total


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    build_index()