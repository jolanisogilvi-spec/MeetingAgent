"""Lightweight in-memory RAG over knowledge-base materials.

Workflow per generation:
  1. Parse each knowledge-base file (txt/docx) to text.
  2. Sliding-window chunk the text.
  3. Embed all chunks once via the embedding service.
  4. Embed the query (meeting text), compute cosine similarity, return top-K.

There is no persistence — the index is rebuilt every generation. This matches
the first-version scope from ARCHITECTURE.md (no FAISS, numpy only).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import embedding as embedding_service
from .file_parser import chunk_text, parse_file

CHUNK_SIZE = 500
CHUNK_OVERLAP = 80
QUERY_CHAR_BUDGET = 4000


@dataclass
class KBChunk:
    source: str
    text: str


@dataclass
class KBIndex:
    chunks: list[KBChunk]
    matrix: np.ndarray  # shape (n_chunks, dim); empty array if no chunks

    @property
    def empty(self) -> bool:
        return not self.chunks or self.matrix.size == 0


def build_index(
    file_paths: list[str | Path],
    *,
    api_key: str,
    base_url: str | None,
    model: str,
) -> KBIndex:
    """Parse + chunk + embed every file. Returns an empty index if no chunks."""
    chunks: list[KBChunk] = []
    for fp in file_paths:
        p = Path(fp)
        if not p.exists():
            continue
        try:
            text = parse_file(p)
        except Exception:
            continue
        for piece in chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP):
            chunks.append(KBChunk(source=p.name, text=piece))

    if not chunks:
        return KBIndex(chunks=[], matrix=np.zeros((0, 0), dtype=np.float32))

    vectors = embedding_service.embed(
        api_key=api_key,
        base_url=base_url,
        model=model,
        texts=[c.text for c in chunks],
    )
    matrix = np.array(vectors, dtype=np.float32)
    matrix = _normalize(matrix)
    return KBIndex(chunks=chunks, matrix=matrix)


def retrieve(
    index: KBIndex,
    query: str,
    *,
    api_key: str,
    base_url: str | None,
    model: str,
    top_k: int = 5,
) -> list[KBChunk]:
    """Return the top-K most similar chunks. Empty list if index is empty."""
    if index.empty or not query.strip():
        return []
    trimmed = query[:QUERY_CHAR_BUDGET]
    vectors = embedding_service.embed(
        api_key=api_key,
        base_url=base_url,
        model=model,
        texts=[trimmed],
    )
    q = np.array(vectors[0], dtype=np.float32)
    q = _normalize(q.reshape(1, -1))[0]
    if q.shape[0] != index.matrix.shape[1]:
        return []
    sims = index.matrix @ q
    k = min(top_k, len(index.chunks))
    top_idx = np.argsort(-sims)[:k]
    return [index.chunks[int(i)] for i in top_idx]


def format_context(snippets: list[KBChunk], char_budget: int = 3000) -> str:
    """Render retrieved chunks for prompt injection, with file attribution."""
    if not snippets:
        return ""
    pieces: list[str] = []
    used = 0
    for idx, snip in enumerate(snippets, start=1):
        header = f"[片段{idx}] 来源：{snip.source}\n"
        body = snip.text.strip()
        block = header + body
        if used + len(block) > char_budget and pieces:
            break
        pieces.append(block)
        used += len(block)
    return "\n\n".join(pieces)


def _normalize(matrix: np.ndarray) -> np.ndarray:
    if matrix.size == 0:
        return matrix
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    return matrix / norms
