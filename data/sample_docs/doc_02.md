# Load Balancing Algorithms

Load balancers distribute incoming network traffic across multiple backend servers to ensure no single server becomes overwhelmed. Round robin is the simplest algorithm, cycling through servers sequentially regardless of their current load.

Weighted round robin assigns a weight to each server based on its capacity, sending proportionally more requests to higher-capacity servers. Least connections routing sends new requests to whichever server currently has the fewest active connections, which works well when requests have variable processing times.

IP hash algorithms compute a hash of the client's IP address to consistently route the same client to the same backend server, useful for maintaining session affinity without shared session storage. Layer 4 load balancers operate at the transport layer and route based on IP and port, while Layer 7 load balancers operate at the application layer and can route based on HTTP headers, cookies, or URL paths.

Health checks are essential for load balancers to detect and route around failed servers. Active health checks periodically probe servers, while passive health checks monitor real traffic for failures.
