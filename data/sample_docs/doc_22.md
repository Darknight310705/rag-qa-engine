# Event Sourcing

Event sourcing is an architectural pattern where instead of storing only the current state of an entity, every change to that entity is stored as an immutable sequence of events, and the current state is derived by replaying those events in order. This differs fundamentally from traditional CRUD persistence, where an update overwrites the previous state and that history is lost unless explicitly logged elsewhere.

Because the full history of changes is preserved, event sourcing naturally supports audit logging, temporal queries (what was the state of this entity at a given point in time), and debugging production issues by replaying the exact sequence of events that led to a bug. It also enables rebuilding read models from scratch by replaying the event log, which is useful when a new view of the data is needed that wasn't anticipated when the system was originally built.

Event sourcing is frequently paired with CQRS (Command Query Responsibility Segregation), which separates the write model (the event log) from one or more read models optimized for specific query patterns, since the event log itself is rarely efficient to query directly. The main costs are increased system complexity, the need for careful event schema versioning as the system evolves, and the operational overhead of managing potentially large and ever-growing event stores.
