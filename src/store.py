"""
Shared configuration for the embedding + vector-store layer (Milestone 4).

Centralizes the embedding model and the ChromaDB client/collection so the
embed and retrieve modules stay consistent. The model and client are created
lazily and cached, so importing this module is cheap and the (~130 MB) model
only downloads/loads the first time it is actually needed.

Embedding model: BAAI/bge-small-en-v1.5 (per planning.md Retrieval Approach).
It accepts up to 512 tokens, matching the ~380-word chunk cap from ingestion.
BGE recommends prefixing *queries* (not passages) with a short instruction.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHUNKS_PATH = PROJECT_ROOT / "data" / "processed" / "chunks.jsonl"
CHROMA_PATH = PROJECT_ROOT / "chroma_db"

COLLECTION_NAME = "guide_chunks"
MODEL_NAME = "BAAI/bge-small-en-v1.5"
# Instruction BGE-v1.5 expects on the query side only.
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

_model = None
_client = None


def get_model():
    """Load (once) and return the SentenceTransformer embedding model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_passages(texts: list[str]) -> list[list[float]]:
    """Embed chunk texts (no query prefix). Normalized for cosine similarity."""
    vectors = get_model().encode(
        texts, normalize_embeddings=True, show_progress_bar=False
    )
    return vectors.tolist()


def embed_query(text: str) -> list[float]:
    """Embed a search query, applying BGE's recommended query instruction."""
    vector = get_model().encode(
        [QUERY_PREFIX + text], normalize_embeddings=True, show_progress_bar=False
    )[0]
    return vector.tolist()


def get_client():
    """Return a persistent ChromaDB client (data stored under chroma_db/)."""
    global _client
    if _client is None:
        import chromadb
        _client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return _client


def get_collection():
    """Get or create the chunk collection, using cosine distance."""
    return get_client().get_or_create_collection(
        name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )