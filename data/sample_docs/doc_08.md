# Cross-Encoder Reranking

While bi-encoder models like sentence transformers encode queries and documents independently into fixed vectors, allowing fast approximate nearest neighbor search, cross-encoder models jointly encode a query-document pair in a single forward pass through a transformer, producing a more accurate relevance score at the cost of much higher computational expense.

Because cross-encoders cannot be precomputed and indexed the way bi-encoder embeddings can, they are impractical to run over an entire large corpus for every query. Instead, they are typically used as a second-stage reranker: a fast bi-encoder or BM25 retrieval step first narrows a large corpus down to a small candidate set, often the top 50 to 100 documents, and the cross-encoder then reranks only this smaller set.

This two-stage retrieve-then-rerank pipeline is a standard pattern in modern information retrieval systems, balancing the speed of approximate retrieval with the accuracy of full attention-based relevance scoring.
