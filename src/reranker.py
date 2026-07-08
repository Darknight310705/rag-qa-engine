"""
Cross-encoder reranking: the second stage of the retrieve-then-rerank
pipeline. Hybrid retrieval (dense + BM25) narrows the corpus down to a
small candidate set; this module scores each (query, candidate) pair
jointly through a cross-encoder for a much more accurate relevance signal
than cosine similarity alone, then returns the candidates re-sorted.
"""
from typing import List, Tuple

from sentence_transformers import CrossEncoder

from src.config import RERANKER_MODEL_NAME

_reranker_cache = {}


def get_reranker() -> CrossEncoder:
    if "model" not in _reranker_cache:
        _reranker_cache["model"] = CrossEncoder(RERANKER_MODEL_NAME)
    return _reranker_cache["model"]


def rerank(query: str, candidates: List[str], top_k: int) -> List[Tuple[int, float]]:
    """
    candidates: list of chunk texts (already deduplicated).
    Returns list of (original_index, rerank_score), sorted best-first,
    truncated to top_k.
    """
    if not candidates:
        return []
    model = get_reranker()
    pairs = [(query, c) for c in candidates]
    scores = model.predict(pairs)
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    return [(idx, float(score)) for idx, score in ranked[:top_k]]
