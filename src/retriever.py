"""
Hybrid retrieval pipeline: dense (FAISS) + sparse (BM25) candidate
generation, score fusion, then cross-encoder reranking.

Pipeline:
  1. Dense search over FAISS  -> DENSE_TOP_K candidates
  2. BM25 search               -> BM25_TOP_K candidates
  3. Union candidates, fuse normalized scores (weighted by HYBRID_ALPHA)
  4. Cross-encoder reranks the fused candidate set -> RERANK_TOP_K final chunks
"""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

from src import vector_index, bm25_index, reranker
from src.config import (
    FAISS_INDEX_PATH,
    BM25_INDEX_PATH,
    CHUNK_STORE_PATH,
    DENSE_TOP_K,
    BM25_TOP_K,
    RERANK_TOP_K,
    HYBRID_ALPHA,
)


@dataclass
class RetrievedChunk:
    chunk_id: str
    doc_id: str
    text: str
    dense_score: float
    bm25_score: float
    fused_score: float
    rerank_score: float = 0.0


def _min_max_normalize(scores: List[float]) -> List[float]:
    if not scores:
        return []
    lo, hi = min(scores), max(scores)
    if hi - lo < 1e-9:
        return [0.0 for _ in scores]
    return [(s - lo) / (hi - lo) for s in scores]


class HybridRetriever:
    def __init__(self):
        self.faiss_index = vector_index.load_index(FAISS_INDEX_PATH)
        self.bm25 = bm25_index.load_bm25_index(BM25_INDEX_PATH)
        self.chunks = self._load_chunk_store(CHUNK_STORE_PATH)

    @staticmethod
    def _load_chunk_store(path: Path):
        chunks = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                chunks.append(json.loads(line))
        return chunks

    def retrieve(self, query: str, top_k: int = RERANK_TOP_K, use_reranker: bool = True) -> List[RetrievedChunk]:
        # --- Dense candidates ---
        query_embedding = vector_index.embed_texts([query])[0]
        dense_scores, dense_indices = vector_index.search(self.faiss_index, query_embedding, DENSE_TOP_K)

        # --- BM25 candidates ---
        bm25_indices, bm25_scores = bm25_index.search(self.bm25, query, BM25_TOP_K)

        # --- Union + score fusion ---
        candidate_indices = set(int(i) for i in dense_indices if i != -1) | set(bm25_indices)

        dense_score_map = {int(i): float(s) for i, s in zip(dense_indices, dense_scores) if i != -1}
        bm25_score_map = {int(i): float(s) for i, s in zip(bm25_indices, bm25_scores)}

        norm_dense = _min_max_normalize([dense_score_map.get(i, 0.0) for i in candidate_indices])
        norm_bm25 = _min_max_normalize([bm25_score_map.get(i, 0.0) for i in candidate_indices])

        fused: List[RetrievedChunk] = []
        for idx, nd, nb in zip(candidate_indices, norm_dense, norm_bm25):
            chunk = self.chunks[idx]
            fused_score = HYBRID_ALPHA * nd + (1 - HYBRID_ALPHA) * nb
            fused.append(
                RetrievedChunk(
                    chunk_id=chunk["chunk_id"],
                    doc_id=chunk["doc_id"],
                    text=chunk["text"],
                    dense_score=dense_score_map.get(idx, 0.0),
                    bm25_score=bm25_score_map.get(idx, 0.0),
                    fused_score=fused_score,
                )
            )

        fused.sort(key=lambda c: c.fused_score, reverse=True)

        if not use_reranker:
            return fused[:top_k]

        # --- Cross-encoder rerank over the fused candidate set ---
        candidate_pool = fused[: max(DENSE_TOP_K, BM25_TOP_K)]
        rerank_results = reranker.rerank(query, [c.text for c in candidate_pool], top_k=top_k)

        final: List[RetrievedChunk] = []
        for idx, score in rerank_results:
            chunk = candidate_pool[idx]
            chunk.rerank_score = score
            final.append(chunk)
        return final
