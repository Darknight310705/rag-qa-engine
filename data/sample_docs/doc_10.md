# Evaluation Metrics for Information Retrieval

Recall@k measures the proportion of relevant documents that appear within the top k results returned by a retrieval system, and is one of the most common metrics for evaluating retrieval quality. Precision@k measures the proportion of the top k results that are actually relevant.

Mean Reciprocal Rank (MRR) evaluates ranking quality by taking the reciprocal of the rank position of the first relevant result for each query, then averaging across all queries; MRR rewards systems that place a relevant result near the top of the ranked list. Normalized Discounted Cumulative Gain (nDCG) accounts for both relevance and position of results, applying a logarithmic discount to results that appear lower in the ranking.

For retrieval-augmented generation systems specifically, faithfulness metrics assess whether the generated answer is actually supported by the retrieved context, rather than being fabricated or hallucinated. Answer relevance metrics separately assess whether the generated answer actually addresses the user's original question.
