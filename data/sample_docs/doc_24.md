# Database Sharding Strategies

Sharding partitions a large database horizontally across multiple physical servers, with each shard holding a subset of the total data, allowing a dataset too large or too high-throughput for a single machine to be distributed across many machines. This differs from replication, where each server holds a full copy of the data; sharding and replication are often combined, with each shard itself replicated for fault tolerance.

Range-based sharding assigns contiguous ranges of the shard key to each shard, which makes range queries efficient but can create hotspots if writes cluster around a particular range, such as sequentially increasing IDs or timestamps. Hash-based sharding applies a hash function to the shard key to distribute rows more evenly across shards, avoiding hotspots but making range queries across shards inefficient since related rows are scattered.

Choosing a shard key is one of the most consequential decisions in a sharded system's design, since it's difficult to change later without a significant data migration. A poorly chosen shard key can lead to "hot shards" that receive disproportionate traffic, or force cross-shard queries and joins that are expensive or require application-level coordination across multiple database connections.
