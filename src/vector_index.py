"""
FAISS-backed dense vector index.

Uses an IndexFlatIP (exact inner-product search over L2-normalized vectors,
i.e. exact cosine similarity) as the default -- correct and simple, and
fast enough for corpora up to a few hundred thousand chunks. For larger
corpora, swap IndexFlatIP for IndexIVFFlat (see build_ivf_index below) to
trade a small amount of recall for much lower query latency at scale.
"""
from pathlib import Path
from typing import List, Tuple

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from src.config import EMBEDDING_MODEL_NAME, EMBEDDING_DIM

_model_cache = {}


def get_embedding_model() -> SentenceTransformer:
    if "model" not in _model_cache:
        _model_cache["model"] = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model_cache["model"]


def embed_texts(texts: List[str]) -> np.ndarray:
    model = get_embedding_model()
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,  # pre-normalize -> inner product == cosine similarity
    )
    return embeddings.astype("float32")


def build_flat_index(embeddings: np.ndarray) -> faiss.Index:
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index


def build_ivf_index(embeddings: np.ndarray, n_clusters: int = 100) -> faiss.Index:
    """
    Use this instead of build_flat_index once the corpus grows large
    (roughly >100k chunks) and exact search becomes too slow.
    n_clusters should scale roughly as sqrt(n_vectors).
    """
    dim = embeddings.shape[1]
    quantizer = faiss.IndexFlatIP(dim)
    index = faiss.IndexIVFFlat(quantizer, dim, n_clusters, faiss.METRIC_INNER_PRODUCT)
    index.train(embeddings)
    index.add(embeddings)
    index.nprobe = min(10, n_clusters)
    return index


def save_index(index: faiss.Index, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(path))


def load_index(path: Path) -> faiss.Index:
    return faiss.read_index(str(path))


def search(index: faiss.Index, query_embedding: np.ndarray, top_k: int) -> Tuple[np.ndarray, np.ndarray]:
    """Returns (scores, indices), each shape (top_k,)."""
    scores, indices = index.search(query_embedding.reshape(1, -1), top_k)
    return scores[0], indices[0]
