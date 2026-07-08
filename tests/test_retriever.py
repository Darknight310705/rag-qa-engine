"""
Unit tests for chunking and score fusion logic. These don't require the
embedding model to be downloaded, so they run fast and are safe for CI.

Run with:  pytest tests/
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.chunking import split_into_sentences, chunk_document
from src.retriever import _min_max_normalize


def test_split_into_sentences_basic():
    text = "This is one sentence. This is another! Is this a question?"
    sentences = split_into_sentences(text)
    assert len(sentences) == 3
    assert sentences[0] == "This is one sentence."


def test_split_into_sentences_empty():
    assert split_into_sentences("") == []
    assert split_into_sentences("   ") == []


def test_chunk_document_produces_chunks():
    text = "# Title\n\n" + " ".join([f"Sentence number {i}." for i in range(1, 200)])
    chunks = chunk_document("test_doc", text)
    assert len(chunks) > 1
    assert all(c.doc_id == "test_doc" for c in chunks)
    assert chunks[0].chunk_id == "test_doc::chunk_0"
    # title should be prepended to give each chunk standalone context
    assert "Title" in chunks[0].text


def test_chunk_document_empty_body():
    assert chunk_document("empty_doc", "# Just a title\n\n") == []


def test_min_max_normalize_uniform_range():
    result = _min_max_normalize([1.0, 2.0, 3.0])
    assert result[0] == 0.0
    assert result[-1] == 1.0
    assert 0.0 < result[1] < 1.0


def test_min_max_normalize_constant_values():
    # all equal scores shouldn't divide by zero
    result = _min_max_normalize([5.0, 5.0, 5.0])
    assert result == [0.0, 0.0, 0.0]


def test_min_max_normalize_empty():
    assert _min_max_normalize([]) == []


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
