"""
Central configuration for the RAG QA Engine.
All tunable parameters live here so behavior can be adjusted without
touching pipeline logic.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Data / index paths -----------------------------------------------
DATA_DIR = BASE_DIR / "data" / "sample_docs"
INDEX_DIR = BASE_DIR / "data" / "index"
FAISS_INDEX_PATH = INDEX_DIR / "faiss.index"
BM25_INDEX_PATH = INDEX_DIR / "bm25.pkl"
CHUNK_STORE_PATH = INDEX_DIR / "chunks.jsonl"

# --- Chunking -----------------------------------------------------------
CHUNK_SIZE_TOKENS = 180          # target chunk size
CHUNK_OVERLAP_TOKENS = 40        # overlap between consecutive chunks

# --- Embedding model ------------------------------------------------------
# all-MiniLM-L6-v2 is a good default: 384-dim, fast, strong quality/speed tradeoff.
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DIM = 384

# --- Reranker -------------------------------------------------------------
RERANKER_MODEL_NAME = os.getenv("RERANKER_MODEL_NAME", "cross-encoder/ms-marco-MiniLM-L-6-v2")

# --- Hybrid retrieval weighting --------------------------------------------
# final_score = ALPHA * normalized_dense_score + (1 - ALPHA) * normalized_bm25_score
HYBRID_ALPHA = 0.5
DENSE_TOP_K = 20          # candidates pulled from FAISS
BM25_TOP_K = 20           # candidates pulled from BM25
RERANK_TOP_K = 5          # final number of chunks passed to the LLM

# --- Generation -------------------------------------------------------------
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GENERATION_MODEL = os.getenv("GENERATION_MODEL", "claude-sonnet-4-6")
MAX_GENERATION_TOKENS = 800

# --- Auth -------------------------------------------------------------------
JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_ME_IN_PRODUCTION")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_MINUTES = 30
JWT_REFRESH_EXPIRY_DAYS = 7

# --- Rate limiting ------------------------------------------------------------
RATE_LIMIT_REQUESTS_PER_MINUTE = 30
