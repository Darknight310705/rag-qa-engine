# Content Delivery Networks

A Content Delivery Network (CDN) is a geographically distributed network of proxy servers that cache and serve content from locations physically closer to end users, reducing latency compared to serving every request from a single origin server. When a user requests content, the CDN's DNS routing directs them to the nearest edge server with a cached copy, or fetches it from the origin and caches it for subsequent requests if it's not already cached.

Cache-Control headers set by the origin server determine how long a CDN edge node is allowed to serve a cached copy before revalidating with the origin, commonly expressed as a max-age value in seconds. Cache invalidation, purging stale content across all edge nodes when the origin content changes, remains one of the notoriously hard problems in distributed systems, since it requires propagating the invalidation to every edge location, some of which may be temporarily unreachable.

Beyond static asset caching, modern CDNs increasingly run compute at the edge, executing small functions close to the user for use cases like A/B testing, authentication checks, or personalization, without requiring a round trip to the origin server for logic that doesn't need centralized data.
