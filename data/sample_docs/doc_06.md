# Rate Limiting Strategies

Rate limiting controls the number of requests a client can make to an API within a given time window, protecting backend services from being overwhelmed and ensuring fair resource usage among clients. The token bucket algorithm maintains a bucket of tokens that refills at a fixed rate; each request consumes a token, and requests are rejected when the bucket is empty.

The leaky bucket algorithm processes requests at a fixed output rate regardless of burstiness in the input, smoothing traffic spikes. Fixed window counters simply count requests within a fixed time interval, such as 100 requests per minute, but can allow bursts at window boundaries.

Sliding window algorithms address the boundary problem by considering a rolling time window rather than fixed intervals, providing more consistent rate limiting behavior. Distributed rate limiting across multiple API server instances typically requires a shared store like Redis to track request counts consistently across the fleet.
