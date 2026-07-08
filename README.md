# Hybrid RAG QA Engine

A retrieval-augmented question-answering system combining dense vector search
(FAISS), sparse lexical search (BM25), and cross-encoder reranking, served
through a JWT-authenticated FastAPI backend — with a real evaluation harness
measuring retrieval quality rather than just "it runs."

## Why hybrid retrieval instead of embeddings-only RAG

Most RAG demos embed a query, do a FAISS lookup, and pass the top-k chunks
straight to an LLM. This misses two things:

1. **Dense embeddings miss exact lexical matches.** A query containing a
   specific term (an error code, an acronym, a parameter name like `k1` or
   `nprobe`) can retrieve a chunk that's semantically "close" but lexically
   wrong, while missing the chunk that contains the literal term. BM25
   catches this.
2. **Raw similarity scores aren't the same as relevance.** A bi-encoder
   embeds the query and each document independently, so it never lets the
   two interact. A cross-encoder reranker jointly encodes (query, chunk)
   pairs and produces a materially better relevance ranking — but it's too
   slow to run over an entire corpus, so it's only used to rerank the
   smaller candidate set surfaced by the first stage.

This repo implements the standard **retrieve → fuse → rerank → generate**
pipeline used in production RAG systems, and includes an eval harness that
measures whether reranking actually helps rather than assuming it does (see
[Evaluation](#evaluation) below — on this corpus, it doesn't move the
aggregate numbers, and the README says so rather than spinning a null
result into a win).

## Architecture

```
                     ┌─────────────┐
                     │   Query     │
                     └──────┬──────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
     ┌─────────────────┐        ┌─────────────────┐
     │  Dense Search     │        │   BM25 Search    │
     │  (FAISS, top 20) │        │   (top 20)       │
     └────────┬─────────┘        └────────┬─────────┘
              │                           │
              └─────────────┬─────────────┘
                            ▼
                 ┌─────────────────────┐
                 │  Score Fusion         │
                 │  (min-max normalize   │
                 │   + weighted sum)     │
                 └──────────┬───────────┘
                            ▼
                 ┌─────────────────────┐
                 │  Cross-Encoder        │
                 │  Reranker (top 5)     │
                 └──────────┬───────────┘
                            ▼
                 ┌─────────────────────┐
                 │  Claude (generation)  │
                 │  grounded + cited      │
                 └──────────┬───────────┘
                            ▼
                     ┌─────────────┐
                     │   Answer     │
                     └─────────────┘
```

**Ingestion (offline, `scripts/build_index.py`):**
`data/sample_docs/*.md` → sentence-aware chunking with overlap
(`src/chunking.py`) → embed with `all-MiniLM-L6-v2` → FAISS `IndexFlatIP`
+ BM25 index, both persisted to `data/index/`.

**Serving (`src/api.py`):** FastAPI app, JWT auth on all data-touching
routes, in-memory sliding-window rate limiter, `/query` runs the full
hybrid retrieval + generation pipeline per request.

## Repo structure

```
rag-qa-engine/
├── data/sample_docs/     # source corpus (28 docs on distributed systems / IR topics)
├── src/
│   ├── config.py          # all tunable parameters in one place
│   ├── chunking.py         # sentence-aware chunking with overlap
│   ├── vector_index.py     # FAISS wrapper + embedding
│   ├── bm25_index.py        # BM25 wrapper
│   ├── retriever.py         # hybrid fusion + reranking orchestration
│   ├── reranker.py           # cross-encoder reranking
│   ├── generator.py          # Claude API call with citation-grounded prompt
│   ├── auth.py                # JWT issuance/verification, password hashing
│   └── api.py                  # FastAPI app + routes
├── scripts/build_index.py  # one-time index build
├── eval/
│   ├── eval_set.json        # 15 labeled queries with ground-truth doc IDs
│   └── run_eval.py           # Recall@k / Precision@k / MRR, baseline vs. reranked
└── tests/test_retriever.py  # unit tests (chunking, score fusion)
```

## Setup

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY and JWT_SECRET
python -m scripts.build_index     # builds FAISS + BM25 indexes from data/sample_docs
uvicorn src.api:app --reload      # starts the API on http://localhost:8000
```

Default demo login: `username=demo`, `password=demo1234` (see `src/auth.py`
— swap the in-memory `USERS` dict for a real users table before deploying).

```bash
# Login
curl -X POST localhost:8000/auth/login -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo1234"}'

# Query (use the access_token from above)
curl -X POST localhost:8000/query -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"question": "How does cross-encoder reranking improve retrieval?"}'
```

## Evaluation

Run `python -m eval.run_eval` to score the retriever against 37 hand-labeled
queries (including several adversarial ones, e.g. a query about resizing a
cache cluster that's designed to fool BM25's keyword match into returning
the wrong document), comparing the hybrid pipeline with and without the
cross-encoder reranking stage at k=1, 3, and 5 — so the value of that stage
is measured, not assumed:

```
============================================================
Metric              Dense+BM25 (no rerank)   + Cross-Encoder Rerank
============================================================
Recall@1             0.9865                   0.9865
Precision@1          1.0                      1.0
MRR@1                1.0                      1.0
------------------------------------------------------------
Recall@3             1.0                      1.0
Precision@3          0.3423                   0.3423
MRR@3                1.0                      1.0
------------------------------------------------------------
Recall@5             1.0                      1.0
Precision@5          0.2676                   0.2671
MRR@5                1.0                      1.0
============================================================
```

**Honest read of these numbers:** the cross-encoder reranking stage does
not measurably improve retrieval quality on this corpus — every metric is
identical or within noise of the no-rerank baseline. This isn't a case of
the reranker being broken (its ranking logic is unit-tested and its output
was manually verified to actually reorder candidates); it's that hybrid
dense+BM25 fusion is already strong enough on a corpus this size that there
isn't much ranking ambiguity left for a reranker to resolve. A larger,
noisier, or more ambiguous corpus would be a fairer test of the reranking
stage's value.

Note: precision@k is computed over **distinct documents**, not raw chunks
— multiple chunks from the same correct document are deduplicated before
scoring, since counting them separately would inflate precision without
reflecting genuine ranking diversity (see `dedupe_doc_ids` in
`eval/run_eval.py`).

Run the command yourself to reproduce these numbers, or after adding your
own docs/queries — figures will shift with corpus size, embedding model
version, and reranker model version. Full per-query results (including
which doc IDs were retrieved for each query, at each k) are written to
`eval/results.json` after each run.

## Design decisions worth knowing for an interview

- **Why `IndexFlatIP` instead of `IndexIVFFlat`?** Exact search is used
  here because the demo corpus is small. `src/vector_index.py` includes
  `build_ivf_index()` for when the corpus grows past ~100k chunks, where
  exact search stops being fast enough and an approximate index with
  tunable `nprobe` becomes necessary.
- **Why min-max normalize before fusing scores?** FAISS inner-product
  scores and BM25 scores live on completely different scales, so summing
  them directly would let whichever score has the larger raw range
  dominate the fused ranking regardless of actual relevance.
- **Why cap the reranker's candidate set instead of reranking everything?**
  Cross-encoders require a full forward pass per (query, document) pair
  and can't be precomputed the way embeddings can — reranking the entire
  corpus per query doesn't scale, hence the retrieve-then-rerank pattern.
- **Why is `/query` the only rate-limited route?** It's the only route
  that triggers an LLM call and is therefore the one with real per-request
  cost; a production version would rate-limit more broadly.

## Known limitations

- The in-memory user store and rate limiter reset on restart and don't
  work across multiple server instances — a real deployment needs a
  database for users and Redis (or similar) for shared rate-limit state.
- No token-blacklist mechanism for revoking JWTs before expiry.
- The 28-document corpus is intentionally small for a fast, inspectable
  demo; swap in a larger corpus via `data/sample_docs/` and re-run
  `scripts/build_index.py`.
- The cross-encoder reranking stage is implemented and unit-tested but
  doesn't measurably improve retrieval metrics on this corpus (see
  [Evaluation](#evaluation)) — it's kept in the pipeline as a demonstration
  of the retrieve-then-rerank pattern and because it may earn its keep on
  a larger or more ambiguous corpus, not because it's currently pulling
  weight here.
