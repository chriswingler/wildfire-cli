# ADR-004: In-Memory State for Active Multiplayer Fire Sessions

*   **Status**: Accepted
*   **Date**: 2024-07-23
*   **Deciders**: Lead Developer (as per `docs/multiplayer-architecture.md`)

## Context

For multiplayer fire incidents, real-time updates and fast interactions are crucial. The full `FireGrid` simulation involves frequent changes and calculations. Persisting every single change of the `FireGrid` to a database in real-time could be slow and complex.

## Decision

Active multiplayer fire sessions, including their full `FireGrid` object and associated `WeatherConditions`, will be managed primarily in-memory within the bot's process.
*   The `WildfireGame` class (or a similar manager class) will hold a dictionary or collection of active fire sessions.
*   The SQLite database (`ADR-003`) will be used for:
    *   Storing summary information about fires (e.g., initial state, overall status).
    *   Tracking persistent aspects like which users have responded.
    *   Potentially periodic snapshots or for persistence across restarts if explicitly designed (the `multiplayer-architecture.md` mentions "Fire state persists across bot restarts via auto-progression timing" which implies some form of saving/loading, though the primary simulation is in-memory).

## Consequences

**Positive**:
*   **Performance**: In-memory access is significantly faster than disk-based database access, allowing for rapid calculations and updates for the fire simulation (e.g., spread, suppression).
*   **Real-time Interaction**: Enables immediate feedback to user actions within the simulation.
*   **Complexity Reduction (for simulation state)**: Avoids complex database operations for every minor change in the simulation grid.
*   **Suitable for Cellular Automata**: Cellular automata states are naturally held and manipulated in memory grids.

**Negative**:
*   **Data Volatility**: If the bot crashes, any active simulation state that hasn't been persisted to the database might be lost. A recovery mechanism or periodic saving strategy is needed to mitigate this.
*   **Memory Usage**: Each active fire simulation consumes memory. This could limit the number of concurrent multiplayer sessions the bot can handle, depending on available system memory and grid size.
*   **Scalability (Single Process)**: If the bot runs as a single process, all in-memory states are confined to that process. Scaling across multiple processes or servers would require a more complex distributed state management solution (e.g., Redis, a dedicated game state server).
*   **State Synchronization (if scaled)**: If the bot were to be sharded or run on multiple instances, synchronizing this in-memory state would be a significant challenge. (Currently assumed to be a single-process bot).

**Mitigation for Data Volatility**:
*   The `multiplayer-architecture.md` mentions "Fire state persists across bot restarts via auto-progression timing." This implies a mechanism exists or is planned to periodically save essential state to allow resumption, reducing data loss on restart.
*   Critical game events (e.g., significant containment, major resource deployment) could still trigger database updates for key summary data.
