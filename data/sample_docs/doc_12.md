# The CAP Theorem

The CAP theorem states that a distributed data store can provide at most two of the following three guarantees simultaneously: Consistency (every read receives the most recent write or an error), Availability (every request receives a non-error response, without guarantee it contains the most recent write), and Partition tolerance (the system continues to operate despite network partitions between nodes).

Because network partitions are unavoidable in real distributed systems, the practical choice in CAP is really between consistency and availability during a partition event: a CP system will refuse requests it cannot guarantee are consistent, while an AP system will continue serving requests using potentially stale data.

Many modern systems don't sit purely on one side of this tradeoff; they offer tunable consistency levels. Cassandra, for example, allows per-query consistency levels ranging from ONE (fast, less consistent) to QUORUM to ALL (slower, strongly consistent), letting application developers make the tradeoff explicit per operation rather than system-wide.

It's worth distinguishing CAP's notion of consistency from ACID consistency in database transactions -- the two use the same word to mean different things, and conflating them is a common source of confusion in distributed systems discussions.
