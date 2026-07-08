# Vector Embeddings and Semantic Search

Vector embeddings are dense numerical representations of text, images, or other data that capture semantic meaning in a continuous vector space. Words or documents with similar meanings are mapped to nearby points in this space, enabling similarity comparisons using metrics like cosine similarity or Euclidean distance.

Sentence transformer models produce fixed-length embeddings for entire sentences or paragraphs, typically ranging from 384 to 1536 dimensions depending on the model. These embeddings can be indexed using approximate nearest neighbor structures such as FAISS's IVF or HNSW indexes to enable fast retrieval over millions of vectors.

Semantic search differs from traditional keyword search because it retrieves documents based on meaning rather than exact term overlap. A query like "how to reduce server costs" can match a document about "cloud infrastructure optimization" even without shared keywords, because their embeddings are close in vector space.

Hybrid search combines dense vector retrieval with sparse keyword-based retrieval like BM25, often improving recall because dense retrieval can miss exact matches on rare terms like product codes or proper nouns, while sparse retrieval can miss semantically related but lexically different content.
