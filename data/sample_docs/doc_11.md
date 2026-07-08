# Consistent Hashing

Consistent hashing is a distributed hashing technique that minimizes the number of keys that need to be remapped when a hash table is resized, which is critical for distributed caches and databases where nodes are frequently added or removed. Both keys and nodes are mapped onto the same hash ring, and a key is assigned to the first node encountered moving clockwise from the key's position.

When a node is added or removed, only the keys that mapped to that specific node need to be redistributed to neighboring nodes, rather than requiring a full remap of every key in the system, as would happen with simple modulo-based hashing. This property makes consistent hashing foundational to distributed systems like DynamoDB, Cassandra, and many CDN routing layers.

Virtual nodes are commonly used to improve load distribution: instead of mapping each physical node to a single point on the hash ring, each physical node is represented by many virtual points scattered around the ring, which smooths out the load imbalance that would otherwise occur when a physical node happens to own a disproportionately large arc of the ring.
