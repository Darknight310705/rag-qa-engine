# Database Indexing

A database index is a data structure that improves the speed of data retrieval operations on a table at the cost of additional writes and storage space. The most common type is the B-tree index, which maintains sorted data and allows searches, sequential access, insertions, and deletions in logarithmic time.

Hash indexes are another common type, offering O(1) average lookup time for equality comparisons but no support for range queries. PostgreSQL supports B-tree, Hash, GiST, SP-GiST, GIN, and BRIN index types, each suited to different query patterns.

Composite indexes cover multiple columns and are useful when queries filter on more than one column simultaneously. The order of columns in a composite index matters significantly for query performance, since the index can only be used efficiently for prefixes of the indexed columns.

Over-indexing a table can degrade write performance because every insert, update, or delete must also update all relevant indexes. A common rule of thumb is to index columns used frequently in WHERE clauses, JOIN conditions, and ORDER BY clauses, while avoiding indexes on columns with low cardinality.
