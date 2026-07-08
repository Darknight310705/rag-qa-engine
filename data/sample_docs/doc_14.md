# Circuit Breaker Pattern

The circuit breaker pattern prevents a service from repeatedly attempting an operation that is likely to fail, protecting both the calling service and the struggling downstream service from being overwhelmed by retries during an outage. It is modeled after electrical circuit breakers that trip to stop current flow when a fault is detected.

A circuit breaker has three states. In the closed state, requests flow through normally, while failures are counted. If the failure rate crosses a configured threshold within a time window, the breaker trips to the open state, in which requests fail immediately without even attempting the call, giving the downstream service time to recover. After a cooldown period, the breaker moves to a half-open state, allowing a limited number of test requests through; if those succeed, the breaker closes again, and if they fail, it reopens.

Circuit breakers are typically combined with fallback logic, such as returning cached data or a default response, so that a failing dependency degrades the user experience gracefully rather than causing a hard failure. Libraries like Hystrix (Netflix, now in maintenance mode) and resilience4j popularized this pattern in the Java ecosystem; similar implementations exist for most major languages.
