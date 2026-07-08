"""
One-time (or re-run-on-update) script that:
  1. Loads and chunks every document in data/sample_docs
  2. Embeds all chunks and builds a FAISS index
  3. Builds a BM25 index over the same chunks
  4. Persists everything to data/index/

Run with:  python -m scripts.build_index
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import chunking, vector_index, bm25_index
from src.config import DATA_DIR, FAISS_INDEX_PATH, BM25_INDEX_PATH, CHUNK_STORE_PATH


def main():
    t0 = time.time()
    print(f"[1/4] Loading + chunking documents from {DATA_DIR} ...")
    chunks = chunking.load_and_chunk_directory(DATA_DIR)
    print(f"      -> {len(chunks)} chunks from {len(list(DATA_DIR.glob('*.md')))} documents")

    if not chunks:
        print("No chunks produced. Check that data/sample_docs contains .md files.")
        sys.exit(1)

    print("[2/4] Embedding chunks and building FAISS index ...")
    texts = [c.text for c in chunks]
    embeddings = vector_index.embed_texts(texts)
    faiss_idx = vector_index.build_flat_index(embeddings)
    vector_index.save_index(faiss_idx, FAISS_INDEX_PATH)
    print(f"      -> FAISS index with {faiss_idx.ntotal} vectors saved to {FAISS_INDEX_PATH}")

    print("[3/4] Building BM25 index ...")
    bm25 = bm25_index.build_bm25_index(texts)
    bm25_index.save_bm25_index(bm25, BM25_INDEX_PATH)
    print(f"      -> BM25 index saved to {BM25_INDEX_PATH}")

    print("[4/4] Writing chunk store ...")
    CHUNK_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CHUNK_STORE_PATH, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps({"chunk_id": c.chunk_id, "doc_id": c.doc_id, "text": c.text}) + "\n")
    print(f"      -> {len(chunks)} chunks written to {CHUNK_STORE_PATH}")

    print(f"\nDone in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
