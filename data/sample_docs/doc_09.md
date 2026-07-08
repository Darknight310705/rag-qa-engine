# Text Chunking Strategies for RAG

Chunking is the process of splitting long documents into smaller segments before embedding them for retrieval, and the chunking strategy significantly affects retrieval quality in retrieval-augmented generation systems. Fixed-size chunking splits text into segments of a set number of tokens or characters, which is simple to implement but can split sentences or ideas mid-thought.

Sentence-aware chunking respects sentence boundaries, avoiding mid-sentence splits, and is often combined with a target chunk size measured in tokens. Recursive character splitting attempts to split on paragraph breaks first, falling back to sentence breaks, then word breaks, only when a segment exceeds the target size.

Semantic chunking groups sentences based on embedding similarity, placing a chunk boundary where consecutive sentences show a significant drop in semantic similarity. Overlapping chunks, where consecutive chunks share a portion of their content, help prevent important context from being split across a chunk boundary and lost during retrieval.

Chunk size involves a tradeoff: smaller chunks improve retrieval precision by allowing more targeted matches, but may lack sufficient context for generation, while larger chunks provide more context but can dilute the embedding's specificity.
