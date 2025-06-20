# ADR-002: Use of Cellular Automata for Fire Simulation

*   **Status**: Accepted
*   **Date**: 2024-07-23
*   **Deciders**: Project Originators / Lead Developer

## Context

A core requirement of the Wildfire Bot is to simulate fire spread in a dynamic way, considering factors like terrain, weather, and fuel. The simulation needs to be computationally feasible for a bot environment and provide engaging gameplay.

## Decision

A 2D cellular automaton model will be used for the fire simulation engine (`src/fire_engine.py`).
*   The game world is represented as a grid of cells.
*   Each cell has a state (e.g., empty, burning, burned, terrain type, fuel load).
*   Fire spread is determined by rules applied to each cell based on its state and the state of its neighbors, influenced by weather and terrain.

## Consequences

**Positive**:
*   **Simplicity and Power**: Cellular automata are relatively simple to implement but can model complex emergent behaviors.
*   **Computational Efficiency**: Generally efficient for grid-based simulations, suitable for a bot that might handle multiple instances.
*   **Scalability**: The grid size can be adjusted to balance detail and performance.
*   **Natural Fit for Grid Data**: Represents spatial phenomena like fire spread intuitively.
*   **Extensibility**: New rules, cell states, or environmental factors (e.g., different suppression techniques) can be added.
*   **Educational Value**: The underlying mechanics are understandable and can be explained to players.

**Negative**:
*   **Abstraction of Reality**: It's a simplified model and doesn't capture all complexities of real-world fire dynamics (e.g., fluid dynamics of heat, precise spotting).
*   **Grid Artifacts**: Behavior can sometimes be influenced by the grid structure (e.g., fire spreading preferentially along axes).
*   **Parameter Tuning**: Spread probabilities and effects of weather/terrain require careful tuning to feel realistic and balanced.
*   **Deterministic (potentially)**: Without sufficient randomness or complexity in rules, simulations might become predictable. (The current model incorporates randomness in weather, spread probability, etc.)
*   **Limited Off-Grid Effects**: Phenomena that don't easily map to a grid (e.g., embers carried long distances by wind creating spot fires far from the main fire front) are harder to model accurately.
