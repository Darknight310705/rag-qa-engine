"""
Sentence-aware chunking with overlap.

Rather than splitting on a fixed number of characters (which can cut a
sentence in half and hand the embedding model a broken thought), we split
on sentence boundaries and greedily pack sentences into chunks up to a
target token budget, carrying a small overlap forward so context isn't
lost at chunk edges.
"""
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

from src.config import CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z(])")


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    text: str
    position: int  # order of this chunk within its source document


def _approx_token_count(text: str) -> int:
    # Cheap approximation: ~0.75 words per token inverse -> use word count as proxy.
    return len(text.split())


def split_into_sentences(text: str) -> List[str]:
    text = re.sub(r"\s+", " ", text.strip())
    if not text:
        return []
    sentences = _SENTENCE_SPLIT_RE.split(text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_document(doc_id: str, raw_text: str) -> List[Chunk]:
    """
    Strip markdown headers, split into sentences, then greedily pack
    sentences into chunks of ~CHUNK_SIZE_TOKENS, carrying the last
    CHUNK_OVERLAP_TOKENS worth of sentences forward into the next chunk.
    """
    # Strip markdown header lines (e.g. "# Title") but keep the title as context
    lines = raw_text.strip().splitlines()
    title = ""
    body_lines = []
    for line in lines:
        if line.startswith("#") and not title:
            title = line.lstrip("#").strip()
        else:
            body_lines.append(line)
    body = " ".join(l.strip() for l in body_lines if l.strip())

    sentences = split_into_sentences(body)
    if not sentences:
        return []

    chunks: List[Chunk] = []
    current: List[str] = []
    current_tokens = 0
    position = 0

    def flush():
        nonlocal current, current_tokens, position
        if not current:
            return
        text = (f"{title}. " if title else "") + " ".join(current)
        chunks.append(
            Chunk(
                chunk_id=f"{doc_id}::chunk_{position}",
                doc_id=doc_id,
                text=text,
                position=position,
            )
        )
        position += 1

    for sentence in sentences:
        sent_tokens = _approx_token_count(sentence)
        if current and current_tokens + sent_tokens > CHUNK_SIZE_TOKENS:
            flush()
            # carry overlap forward: keep last few sentences whose combined
            # token count is closest to CHUNK_OVERLAP_TOKENS
            overlap_sentences = []
            overlap_tokens = 0
            for s in reversed(current):
                t = _approx_token_count(s)
                if overlap_tokens + t > CHUNK_OVERLAP_TOKENS:
                    break
                overlap_sentences.insert(0, s)
                overlap_tokens += t
            current = overlap_sentences
            current_tokens = overlap_tokens

        current.append(sentence)
        current_tokens += sent_tokens

    flush()
    return chunks


def load_and_chunk_directory(directory: Path) -> List[Chunk]:
    all_chunks: List[Chunk] = []
    for path in sorted(directory.glob("*.md")):
        raw_text = path.read_text(encoding="utf-8")
        doc_id = path.stem
        all_chunks.extend(chunk_document(doc_id, raw_text))
    return all_chunks
