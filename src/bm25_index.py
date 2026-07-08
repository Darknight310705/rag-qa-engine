"""
BM25 sparse retrieval index, used as the lexical half of hybrid search.
Dense embeddings can miss exact matches on rare terms (error codes, acronyms,
proper nouns); BM25 catches those. See src/retriever.py for how the two
signals are combined.
"""
import pickle
import re
from pathlib import Path
from typing import List, Tuple

from rank_bm25 import BM25Okapi

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> List[str]:
    return _TOKEN_RE.findall(text.lower())


def build_bm25_index(corpus_texts: List[str]) -> BM25Okapi:
    tokenized_corpus = [tokenize(t) for t in corpus_texts]
    return BM25Okapi(tokenized_corpus)


def save_bm25_index(bm25: BM25Okapi, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(bm25, f)


def load_bm25_index(path: Path) -> BM25Okapi:
    with open(path, "rb") as f:
        return pickle.load(f)


def search(bm25: BM25Okapi, query: str, top_k: int) -> Tuple[List[int], List[float]]:
    tokenized_query = tokenize(query)
    scores = bm25.get_scores(tokenized_query)
    # argsort descending, take top_k
    top_indices = scores.argsort()[::-1][:top_k]
    top_scores = [float(scores[i]) for i in top_indices]
    return list(top_indices), top_scores
