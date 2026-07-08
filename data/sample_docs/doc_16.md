# REST vs GraphQL API Design

REST APIs organize functionality around resources, each identified by a URL, with standard HTTP verbs (GET, POST, PUT, DELETE) mapping to operations on those resources. A common pain point with REST is over-fetching, where an endpoint returns more fields than the client needs, and under-fetching, where the client must make multiple round trips to assemble the data it needs from several endpoints.

GraphQL addresses this by exposing a single endpoint with a strongly typed schema, letting clients specify exactly which fields they need in a single query, and allowing the server to resolve nested, related data in one round trip instead of several. This flexibility comes at a cost: because clients can construct arbitrary queries, servers need protections against overly expensive queries, such as query complexity analysis, depth limiting, or persisted queries.

Caching is generally simpler with REST, since HTTP caching can operate at the URL level, while GraphQL responses typically require application-level caching strategies since every query goes to the same endpoint. Many production systems use both: REST for simple, cacheable public APIs, and GraphQL for complex internal data-fetching needs, particularly for front-end teams that need to iterate on data requirements independently of backend changes.
