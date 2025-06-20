# ADR-003: SQLite for Database Storage

*   **Status**: Accepted
*   **Date**: 2024-07-23
*   **Deciders**: Project Originators / Lead Developer

## Context

The Wildfire Bot needs to persist some game data, such as active fire incidents and responder information, across bot restarts and for record-keeping. The database solution should be lightweight, easy to integrate with Python, and suitable for a small to medium-scale bot.

## Decision

SQLite will be used as the database engine for storing persistent game data. The database will be a local file (`wildfire_game.db`). The `aiosqlite` library will be used for asynchronous database access, compatible with `asyncio` used by `discord.py`.

## Consequences

**Positive**:
*   **Simplicity**: Serverless, self-contained, and requires no separate database server process.
*   **Ease of Use**: Python has built-in support for SQLite (`sqlite3`), and `aiosqlite` provides good async integration.
*   **Portability**: The database is a single file, making it easy to back up, move, or deploy.
*   **Sufficient for Scope**: For the current scale and data needs of the bot (tracking active fires, responders), SQLite offers adequate performance and features.
*   **Low Resource Usage**: Ideal for environments where resources might be limited (e.g., small VPS hosting the bot).
*   **Transactional Integrity**: Supports ACID transactions.

**Negative**:
*   **Concurrency Limitations**: SQLite is not designed for high levels of write concurrency. While `aiosqlite` helps with async access, all writes are ultimately serialized. This is generally acceptable for a Discord bot where database interactions are often sequential per user or channel.
*   **Scalability**: Not suitable for very large datasets or applications requiring distributed database capabilities. If the bot grows to a massive scale with many simultaneous complex queries, SQLite might become a bottleneck.
*   **Manual Schema Migrations**: Schema changes typically require manual SQL or custom migration scripts. More complex ORMs or migration tools might be overkill for this project's scale.
*   **Limited Advanced Features**: Lacks some advanced features of larger RDBMS like PostgreSQL or MySQL (e.g., complex replication, stored procedures beyond views/triggers).
*   **Single Point of Failure**: The database is a single file. Corruption or disk failure could lead to data loss if backups are not maintained.
