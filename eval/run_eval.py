"""
Evaluation harness: runs every labeled query in eval_set.json through the
retriever and computes Recall@k, Precision@k, and MRR against the ground-
truth relevant document IDs. Also compares hybrid retrieval (dense + BM25
+ rerank) against a dense-only baseline, so the benefit of each pipeline
stage is measurable rather than assumed.

Run with:  python -m eval.run_eval
"""
import json
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.retriever import HybridRetriever

EVAL_SET_PATH = Path(__file__).resolve().parent / "eval_set.json"

# Metrics are computed at each of these cutoffs. k=1 and k=3 are the
# interesting ones for reranker evaluation: with only 28 docs, Recall@5
# tends to hit a ceiling (the right doc is almost always somewhere in the
# top 5 regardless of reranking), which hides any reranker contribution.
# k=1 asks the harder question: is the single best result actually right?
K_VALUES = [1, 3, 5]
MAX_K = max(K_VALUES)


def recall_at_k(retrieved_doc_ids: List[str], relevant_doc_ids: List[str], k: int) -> float:
    top_k = set(retrieved_doc_ids[:k])
    relevant = set(relevant_doc_ids)
    if not relevant:
        return 0.0
    return len(top_k & relevant) / len(relevant)


def precision_at_k(retrieved_doc_ids: List[str], relevant_doc_ids: List[str], k: int) -> float:
    top_k = retrieved_doc_ids[:k]
    if not top_k:
        return 0.0
    relevant = set(relevant_doc_ids)
    hits = sum(1 for d in top_k if d in relevant)
    return hits / len(top_k)


def reciprocal_rank_at_k(retrieved_doc_ids: List[str], relevant_doc_ids: List[str], k: int) -> float:
    relevant = set(relevant_doc_ids)
    for rank, doc_id in enumerate(retrieved_doc_ids[:k], start=1):
        if doc_id in relevant:
            return 1.0 / rank
    return 0.0


def run_eval(use_reranker: bool) -> dict:
    retriever = HybridRetriever()
    with open(EVAL_SET_PATH, "r", encoding="utf-8") as f:
        eval_set = json.load(f)

    # per-k accumulators, e.g. recalls[1] = [list of per-query recall@1 scores]
    recalls = {k: [] for k in K_VALUES}
    precisions = {k: [] for k in K_VALUES}
    rrs = {k: [] for k in K_VALUES}
    per_query_results = []

    for item in eval_set:
        query = item["query"]
        relevant_doc_ids = item["relevant_doc_ids"]

        # Retrieve once at the largest k; smaller-k metrics are computed by
        # slicing this same ranked list, so all k values reflect one
        # consistent ranking per query.
        retrieved = retriever.retrieve(query, top_k=MAX_K, use_reranker=use_reranker)
        retrieved_doc_ids = [c.doc_id for c in retrieved]

        per_query_entry = {
            "query": query,
            "relevant": relevant_doc_ids,
            "retrieved": retrieved_doc_ids,
        }

        for k in K_VALUES:
            r = recall_at_k(retrieved_doc_ids, relevant_doc_ids, k)
            p = precision_at_k(retrieved_doc_ids, relevant_doc_ids, k)
            rr = reciprocal_rank_at_k(retrieved_doc_ids, relevant_doc_ids, k)

            recalls[k].append(r)
            precisions[k].append(p)
            rrs[k].append(rr)

            per_query_entry[f"recall@{k}"] = round(r, 3)
            per_query_entry[f"precision@{k}"] = round(p, 3)
            per_query_entry[f"mrr@{k}"] = round(rr, 3)

        per_query_results.append(per_query_entry)

    result = {
        "use_reranker": use_reranker,
        "n_queries": len(eval_set),
        "per_query": per_query_results,
    }
    for k in K_VALUES:
        result[f"mean_recall@{k}"] = round(sum(recalls[k]) / len(recalls[k]), 4)
        result[f"mean_precision@{k}"] = round(sum(precisions[k]) / len(precisions[k]), 4)
        result[f"mrr@{k}"] = round(sum(rrs[k]) / len(rrs[k]), 4)

    return result


def main():
    print(f"Running evaluation over eval set (k={K_VALUES}) ...\n")

    baseline = run_eval(use_reranker=False)
    hybrid_reranked = run_eval(use_reranker=True)

    col1_w, col2_w, col3_w = 20, 25, 22
    total_w = col1_w + col2_w + col3_w

    print("=" * total_w)
    print(f"{'Metric':<{col1_w}}{'Dense+BM25 (no rerank)':<{col2_w}}{'+ Cross-Encoder Rerank':<{col3_w}}")
    print("=" * total_w)
    for k in K_VALUES:
        for label, key in (("Recall@", "mean_recall@"), ("Precision@", "mean_precision@"), ("MRR@", "mrr@")):
            metric_name = f"{label}{k}"
            base_val = baseline[f"{key}{k}"]
            rerank_val = hybrid_reranked[f"{key}{k}"]
            print(f"{metric_name:<{col1_w}}{base_val:<{col2_w}}{rerank_val:<{col3_w}}")
        if k != K_VALUES[-1]:
            print("-" * total_w)
    print("=" * total_w)

    out_path = Path(__file__).resolve().parent / "results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"baseline_no_rerank": baseline, "hybrid_reranked": hybrid_reranked}, f, indent=2)
    print(f"\nFull per-query results written to {out_path}")


if __name__ == "__main__":
    main()
