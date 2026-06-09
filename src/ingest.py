"""
Document ingestion and chunking for The Unofficial Guide RAG system.

Pipeline stages 1 and 2 from the architecture diagram in planning.md:

    1. Document Ingestion  -> load_documents()  (reads data/raw/ + sources.csv metadata)
    2. Chunking            -> preprocess() + chunk_text()

Chunking strategy (see planning.md):
    - Target ~300 words per chunk, hard cap ~380 words.
      (380 words ~= 490 tokens, deliberately under the 512-token limit of
      bge-small-en-v1.5 so that overlap added later never pushes a chunk over
      the limit and gets silently truncated at embedding time.)
    - ~60-word overlap between adjacent chunks.
    - Split on paragraph/blank-line boundaries for prose; fall back to
      sentence boundaries where a document has no paragraph structure
      (the info-session transcripts and the slide-deck PDF).

This module uses only the Python standard library so it can run before any
ML dependencies (sentence-transformers, chromadb) are installed.

Run it with:
    python -m src.ingest                 # from the project root
    python src/ingest.py --preview 3     # also print a few sample chunks
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# --------------------------------------------------------------------------- #
# Configuration                                                               #
# --------------------------------------------------------------------------- #

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
SOURCES_CSV = PROJECT_ROOT / "data" / "sources.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "chunks.jsonl"

TARGET_WORDS = 300   # preferred chunk size
MAX_WORDS = 380      # hard cap including overlap (~490 tokens, under bge's 512)
OVERLAP_WORDS = 60   # ~1-2 sentences of overlap between adjacent chunks

# Source types whose .txt files have no semantic line breaks. Their newlines
# are an artifact of transcription (one clause per line) or PDF slide
# extraction (one fragment per line), so we rejoin them into running text and
# let the chunker re-segment on sentence boundaries.
LINE_BROKEN_TYPES = {"txt", "pdf"}

# Lines that are pure GitHub UI chrome on a scraped repository page. Compared
# case-insensitively after stripping surrounding whitespace.
GITHUB_CHROME_LINES = {
    "skip to content", "repository navigation", "code", "issues",
    "pull requests", "agents", "actions", "projects", "security and quality",
    "insights", "owner avatar", "public", "go to file", "name", "t", "T",
    "repository files navigation", "readme", "contributing", "activity",
    "banner", "important", "resources", "stars", "watchers", "forks",
    "report repository", "releases", "packages", "contributors", "languages",
}


@dataclass
class Document:
    """One source document plus its catalog metadata."""
    source_id: str
    title: str
    type: str
    url: str
    text: str


# --------------------------------------------------------------------------- #
# Stage 1 — Document ingestion                                                #
# --------------------------------------------------------------------------- #

def load_documents(raw_dir: Path = RAW_DIR,
                   sources_csv: Path = SOURCES_CSV) -> list[Document]:
    """Load every source listed in sources.csv from data/raw/<id>.txt.

    The CSV is the source of truth for which documents exist and supplies the
    metadata (title, type, url) attached to every chunk. Files that are missing
    or empty are skipped with a warning so the pipeline doesn't fail on corrupt PDFs
    or the empty placeholder sources.
    """
    documents: list[Document] = []
    with sources_csv.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            source_id = (row.get("id") or "").strip()
            if not source_id:
                continue
            txt_path = raw_dir / f"{source_id}.txt"
            if not txt_path.exists():
                print(f"  [skip] {source_id}: no file at {txt_path.name}")
                continue
            text = txt_path.read_text(encoding="utf-8", errors="replace")
            if not text.strip():
                print(f"  [skip] {source_id}: file is empty")
                continue
            documents.append(Document(
                source_id=source_id,
                title=(row.get("title") or "").strip(),
                type=(row.get("type") or "").strip().lower(),
                url=(row.get("url") or "").strip(),
                text=text,
            ))
    return documents


# --------------------------------------------------------------------------- #
# Stage 2a — Preprocessing / cleaning                                         #
# --------------------------------------------------------------------------- #

def preprocess(text: str, doc_type: str) -> str:
    """Clean a raw document into normalized text ready for chunking.

    The cleaning applied depends on the source type, because the corpus is not
    uniformly clean prose (see the Anticipated Challenges section of
    planning.md):

      - github_repo : strip navigation / file-listing / footer chrome.
      - txt / pdf   : transcripts and slide decks broken one fragment per line;
                      rejoin into running text so sentences are whole.
      - everything  : normalize whitespace and drop empty lines, while
                      preserving blank-line paragraph breaks for real prose.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Strip any leftover HTML tags, then unescape entities. Tags are removed
    # first so that escaped angle brackets in code snippets (e.g. "vector&lt;int&gt;")
    # survive tag-stripping and become literal "<"/">" rather than being deleted.
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)

    if doc_type == "github_repo":
        text = _strip_github_chrome(text)
    elif doc_type in LINE_BROKEN_TYPES:
        text = _rejoin_line_broken(text)

    return _normalize_whitespace(text)


def _strip_github_chrome(text: str) -> str:
    """Drop GitHub UI lines from a scraped repository page.

    Keeps only the prose between the "Repository files navigation" marker
    (everything above it is top-nav + the commit/file listing) and the
    "Topics" footer marker (everything below it is stars/contributors/language
    chrome). Within that window, individual chrome lines are still removed.
    """
    lines = text.split("\n")

    # Narrow to the README body if the navigation markers are present.
    try:
        start = next(i for i, ln in enumerate(lines)
                     if ln.strip().lower() == "repository files navigation") + 1
    except StopIteration:
        start = 0
    try:
        end = next(i for i, ln in enumerate(lines)
                   if i > start and ln.strip().lower() == "topics")
    except StopIteration:
        end = len(lines)
    window = lines[start:end]

    kept = []
    for ln in window:
        stripped = ln.strip()
        if not stripped:
            kept.append("")               # keep paragraph breaks
            continue
        if stripped.lower() in GITHUB_CHROME_LINES:
            continue
        # Drop relative-time chrome and the "Stars Last Updated ..." badge row.
        if re.fullmatch(r"\d+\s*(hour|day|week|month|year)s?\s+ago", stripped, re.I):
            continue
        if stripped.lower().startswith("stars last updated"):
            continue
        kept.append(stripped)
    return "\n".join(kept)


def _rejoin_line_broken(text: str) -> str:
    """Rejoin transcripts / slide decks that have one fragment per line.

    These sources have no meaningful line breaks, so we collapse every run of
    lines into a single block of text. The chunker then re-segments it on
    sentence boundaries.
    """
    joined = " ".join(line.strip() for line in text.split("\n") if line.strip())
    return joined


def _normalize_whitespace(text: str) -> str:
    """Collapse repeated spaces and blank lines; keep single paragraph breaks."""
    # Collapse runs of spaces/tabs within a line.
    text = re.sub(r"[ \t]+", " ", text)
    # Strip trailing/leading spaces on each line.
    text = "\n".join(line.strip() for line in text.split("\n"))
    # Collapse 3+ newlines into a single blank line (one paragraph break).
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# --------------------------------------------------------------------------- #
# Stage 2b — Chunking                                                         #
# --------------------------------------------------------------------------- #

_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")


def _word_count(text: str) -> int:
    return len(text.split())


def _split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    return [s.strip() for s in _SENTENCE_BOUNDARY.split(text) if s.strip()]


def _split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def _build_units(text: str, max_words: int) -> list[str]:
    """Break text into the smallest natural units the chunker will pack.

    Prefer paragraphs; if a document has no paragraph structure, or a single
    paragraph is larger than the hard cap, fall back to sentences. As a final
    safety net, any sentence still longer than the cap is split on word count
    so no unit can ever exceed it on its own.
    """
    paragraphs = _split_paragraphs(text)
    raw_units = paragraphs if len(paragraphs) > 1 else _split_sentences(text)

    units: list[str] = []
    for unit in raw_units:
        unit = re.sub(r"\s+", " ", unit).strip()
        if not unit:
            continue
        if _word_count(unit) <= max_words:
            units.append(unit)
            continue
        # Oversized paragraph -> sentences; oversized sentence -> word slices.
        for sentence in _split_sentences(unit):
            words = sentence.split()
            if len(words) <= max_words:
                units.append(sentence)
            else:
                for i in range(0, len(words), max_words):
                    units.append(" ".join(words[i:i + max_words]))
    return units


def chunk_text(text: str,
               target_words: int = TARGET_WORDS,
               max_words: int = MAX_WORDS,
               overlap_words: int = OVERLAP_WORDS) -> list[str]:
    """Split cleaned text into overlapping chunks of ~target_words words.

    Units (paragraphs, or sentences where there are no paragraphs) are packed
    greedily until adding the next would exceed ``target_words``. A ~60-word
    overlap from the tail of the previous chunk is prepended to each chunk; the
    overlap is trimmed if needed so that no final chunk exceeds ``max_words``.
    """
    units = _build_units(text, max_words)
    if not units:
        return []

    # Pack units into base chunks (no overlap yet). Each base chunk is <=
    # target_words for multi-unit chunks, or a single unit up to max_words.
    base_chunks: list[str] = []
    current: list[str] = []
    current_wc = 0
    for unit in units:
        unit_wc = _word_count(unit)
        if current and current_wc + unit_wc > target_words:
            base_chunks.append(" ".join(current))
            current, current_wc = [], 0
        current.append(unit)
        current_wc += unit_wc
    if current:
        base_chunks.append(" ".join(current))

    if overlap_words <= 0 or len(base_chunks) == 1:
        return base_chunks

    # Prepend overlap from the previous base chunk, trimming it so the combined
    # chunk never exceeds the hard cap.
    chunks = [base_chunks[0]]
    for i in range(1, len(base_chunks)):
        base = base_chunks[i]
        room = max(0, max_words - _word_count(base))
        take = min(overlap_words, room)
        if take > 0:
            tail = base_chunks[i - 1].split()[-take:]
            chunks.append(" ".join(tail) + " " + base)
        else:
            chunks.append(base)
    return chunks


# --------------------------------------------------------------------------- #
# Orchestration                                                               #
# --------------------------------------------------------------------------- #

def chunk_document(doc: Document) -> list[dict]:
    """Preprocess and chunk one document, returning chunk records with metadata."""
    cleaned = preprocess(doc.text, doc.type)
    pieces = chunk_text(cleaned)
    records = []
    for index, piece in enumerate(pieces):
        records.append({
            "chunk_id": f"{doc.source_id}_chunk_{index:03d}",
            "source_id": doc.source_id,
            "title": doc.title,
            "type": doc.type,
            "url": doc.url,
            "chunk_index": index,
            "n_chunks": len(pieces),
            "word_count": _word_count(piece),
            "text": piece,
        })
    return records


def run(raw_dir: Path = RAW_DIR,
        sources_csv: Path = SOURCES_CSV,
        output_path: Path = OUTPUT_PATH,
        preview: int = 0) -> list[dict]:
    """Run the full ingest + chunk pipeline and write chunks to JSONL."""
    print(f"Loading documents from {raw_dir.relative_to(PROJECT_ROOT)} ...")
    documents = load_documents(raw_dir, sources_csv)
    print(f"Loaded {len(documents)} documents.\n")

    all_chunks: list[dict] = []
    print(f"{'source':<12}{'type':<14}{'words':>8}{'chunks':>9}")
    print("-" * 43)
    for doc in documents:
        records = chunk_document(doc)
        all_chunks.extend(records)
        cleaned_wc = _word_count(preprocess(doc.text, doc.type))
        print(f"{doc.source_id:<12}{doc.type:<14}{cleaned_wc:>8}{len(records):>9}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        for record in all_chunks:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    # Summary statistics.
    sizes = [c["word_count"] for c in all_chunks]
    print("-" * 43)
    print(f"\nTotal chunks: {len(all_chunks)}")
    if sizes:
        print(f"Chunk size (words): min={min(sizes)} "
              f"avg={sum(sizes) // len(sizes)} max={max(sizes)}")
        over_cap = sum(1 for s in sizes if s > MAX_WORDS)
        print(f"Chunks over the {MAX_WORDS}-word cap: {over_cap}")
    print(f"Wrote {output_path.relative_to(PROJECT_ROOT)}")

    for record in all_chunks[:preview]:
        print(f"\n--- {record['chunk_id']} "
              f"({record['word_count']} words) | {record['title']} ---")
        text = record["text"]
        print(text[:500] + ("..." if len(text) > 500 else ""))

    return all_chunks


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest and chunk source documents.")
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--sources-csv", type=Path, default=SOURCES_CSV)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--preview", type=int, default=0,
                        help="Print this many sample chunks after running.")
    return parser.parse_args()


if __name__ == "__main__":
    # Make stdout UTF-8 safe so previewing chunks with curly quotes/emoji does
    # not crash on a default Windows (cp1252) console.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    args = _parse_args()
    run(raw_dir=args.raw_dir,
        sources_csv=args.sources_csv,
        output_path=args.output,
        preview=args.preview)