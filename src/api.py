"""
FastAPI application exposing the RAG pipeline.

Endpoints:
  POST /auth/login      -> issue access + refresh tokens
  POST /auth/refresh     -> exchange a refresh token for a new access token
  POST /query             -> JWT-protected hybrid retrieval + generation
  GET  /documents         -> list indexed source documents
  POST /feedback          -> record thumbs up/down on an answer (for eval loop)
  GET  /health            -> liveness check

Run with:  uvicorn src.api:app --reload
"""
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Deque, Dict

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from src import auth
from src.config import DATA_DIR, RATE_LIMIT_REQUESTS_PER_MINUTE
from src.retriever import HybridRetriever
from src.generator import generate_answer

app = FastAPI(title="RAG QA Engine", version="1.0.0")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Loaded once at startup; rebuilding the retriever per-request would reload
# the embedding model and both indexes on every call.
_retriever: HybridRetriever | None = None

# --- Simple in-memory sliding-window rate limiter, keyed by user ------------
_request_log: Dict[str, Deque[float]] = defaultdict(deque)


def rate_limit(username: str):
    now = time.time()
    window = _request_log[username]
    while window and now - window[0] > 60:
        window.popleft()
    if len(window) >= RATE_LIMIT_REQUESTS_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again shortly.",
        )
    window.append(now)


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    payload = auth.decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return payload["sub"]


@app.on_event("startup")
def load_retriever():
    global _retriever
    try:
        _retriever = HybridRetriever()
    except FileNotFoundError:
        # Indexes not built yet -- /query will report this clearly instead of crashing startup.
        _retriever = None


# --- Schemas -----------------------------------------------------------------
class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5


class FeedbackRequest(BaseModel):
    query: str
    chunk_ids: list[str]
    helpful: bool


# --- Auth endpoints ------------------------------------------------------------
@app.post("/auth/login")
def login(body: LoginRequest):
    if not auth.authenticate_user(body.username, body.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {
        "access_token": auth.create_access_token(body.username),
        "refresh_token": auth.create_refresh_token(body.username),
        "token_type": "bearer",
    }


@app.post("/auth/refresh")
def refresh(body: RefreshRequest):
    payload = auth.decode_token(body.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
    return {"access_token": auth.create_access_token(payload["sub"]), "token_type": "bearer"}


# --- Core RAG endpoint -----------------------------------------------------------
@app.post("/query")
def query(body: QueryRequest, username: str = Depends(get_current_user)):
    rate_limit(username)

    if _retriever is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Index not built yet. Run `python -m scripts.build_index` first.",
        )

    retrieved = _retriever.retrieve(body.question, top_k=body.top_k)
    result = generate_answer(body.question, retrieved)
    return {
        "question": body.question,
        "answer": result["answer"],
        "sources": result["sources"],
    }


# --- Supporting endpoints -----------------------------------------------------------
@app.get("/documents")
def list_documents(username: str = Depends(get_current_user)):
    docs = sorted(p.stem for p in Path(DATA_DIR).glob("*.md"))
    return {"documents": docs, "count": len(docs)}


@app.post("/feedback")
def feedback(body: FeedbackRequest, username: str = Depends(get_current_user)):
    # In production this writes to a feedback table used to build future
    # eval sets and to detect queries where retrieval is systematically weak.
    print(f"[feedback] user={username} helpful={body.helpful} query={body.query!r} chunks={body.chunk_ids}")
    return {"status": "recorded"}


@app.get("/health")
def health():
    return {"status": "ok", "index_loaded": _retriever is not None}
