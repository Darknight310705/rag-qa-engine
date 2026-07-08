# BM25 Ranking Function

BM25 (Best Matching 25) is a ranking function used by search engines to estimate the relevance of documents to a search query, based on term frequency and inverse document frequency. It is a bag-of-words retrieval function that ranks documents based on query terms appearing in each document, regardless of their proximity within the document.

The BM25 score incorporates term frequency saturation, meaning the contribution of additional occurrences of a term diminishes as the term appears more frequently, controlled by a parameter typically denoted k1. It also includes a document length normalization component, controlled by a parameter b, which adjusts for the fact that longer documents naturally contain more term occurrences.

BM25 remains a strong baseline for information retrieval tasks and is often used alongside dense retrieval methods in hybrid search systems. Its main limitation is that it relies purely on lexical overlap and cannot capture semantic similarity between terms with different surface forms.
