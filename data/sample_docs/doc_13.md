# Message Queues and Asynchronous Processing

Message queues decouple producers and consumers of work, allowing a service to publish a message and continue without waiting for the receiving service to process it. This improves system resilience: if a downstream consumer is temporarily down, messages simply accumulate in the queue rather than causing the producer to fail.

Point-to-point queues deliver each message to exactly one consumer, useful for distributing work items across a pool of workers for load balancing. Publish-subscribe topics instead deliver a copy of each message to every subscriber, useful when multiple independent services need to react to the same event.

Message durability and acknowledgment semantics matter for reliability: at-most-once delivery risks losing messages if a consumer crashes before processing, at-least-once delivery guarantees the message will be processed but may result in duplicates requiring idempotent consumers, and exactly-once delivery is the hardest guarantee to provide and often requires additional deduplication logic even when the underlying broker claims to support it.

Popular message queue systems include RabbitMQ, which implements the AMQP protocol with flexible routing, and Apache Kafka, which is better described as a distributed log than a traditional queue, retaining messages for a configurable period and allowing multiple independent consumer groups to read the same stream at their own pace.
