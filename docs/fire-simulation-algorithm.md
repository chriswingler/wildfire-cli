# Fire Simulation Engine Algorithm

This document details the algorithm used in the Wildfire Bot's fire simulation engine, primarily found in `src/fire_engine.py`. The simulation uses a 2D cellular automata model to represent and evolve a wildfire over a grid.

## Core Concepts

The simulation is built around a grid of `FireCell` objects. Each cell has properties that affect and are affected by the fire.

### 1. Fire Grid (`FireGrid`)

*   **Structure**: A 2D list of `FireCell` objects. The default grid size is 8x8 cells.
*   **Initialization**:
    *   Each cell is assigned a `TerrainType` based on predefined weights (Forest, Grass, Urban, Ridge, Valley).
    *   `WeatherConditions` are initialized randomly for the entire grid.
    *   Each cell represents approximately 10 acres.
*   **Operational Periods**: The simulation progresses in operational periods. With each new period, weather conditions can change, and the fire is allowed to spread multiple times.

### 2. Fire Cell (`FireCell`)

Each cell in the grid has the following key attributes:

*   **`terrain` (TerrainType)**: The type of terrain in the cell (e.g., Forest, Grass). This affects fuel load and spread probability.
*   **`fire_state` (FireState)**: The current state of the cell.
    *   `EMPTY`: No fire.
    *   `BURNING`: Actively on fire.
    *   `BURNED`: Fire has consumed fuel and is out.
    *   `CONTAINED`: Fire was burning but has been successfully suppressed.
*   **`ignition_time`**: Timestamp when the cell ignited.
*   **`contained_time`**: Timestamp when the cell was contained.
*   **`fuel_load`**: An integer representing the amount of combustible material. Calculated based on `TerrainType`.
    *   Grass: 1-3
    *   Forest: 4-8
    *   Urban: 6-10 (represents structures, higher intensity)
    *   Ridge: 2-5
    *   Valley: 3-6
*   **`burn_intensity`**: Set to `fuel_load` when ignited, 0 otherwise.

### 3. Weather Conditions (`WeatherConditions`)

Weather plays a significant role in fire behavior:

*   **Attributes**:
    *   `wind_direction`: (N, NE, E, SE, S, SW, W, NW)
    *   `wind_speed`: (5-25 mph)
    *   `temperature`: (75-105 °F)
    *   `humidity`: (10-60 %)
*   **Fire Danger Rating**: Calculated based on wind speed, temperature, and humidity, resulting in a rating (LOW, MODERATE, HIGH, EXTREME).
*   **Updates**: Weather is re-initialized at the start of each new `operational_period`.

## Simulation Mechanics

### 1. Starting a Fire (`FireGrid.start_fire`)

*   A fire is typically started at a random location near the center of the grid.
*   The initial number of ignited cells depends on the chosen `intensity` (low, moderate, high).

### 2. Fire Spread (`FireGrid.spread_fire`)

This is the core of the simulation loop. For each cell that is currently `BURNING`:

*   It attempts to spread to its 8 adjacent neighbors.
*   A `_calculate_spread_probability` method determines if an adjacent `EMPTY` cell ignites.

#### Spread Probability Calculation (`_calculate_spread_probability`)

The probability of spread from a `source` cell to a `target` cell is influenced by:

1.  **Base Probability**: A starting probability (e.g., 0.3).
2.  **Target Terrain Multipliers**:
    *   Grass: 1.5x (spreads faster)
    *   Forest: 1.0x
    *   Urban: 0.8x (slower spread, but implies higher damage/intensity)
    *   Ridge: 1.2x (uphill spread)
    *   Valley: 0.7x (can act as barriers)
3.  **Wind**:
    *   If spread direction aligns with wind direction, probability increases proportionally to `wind_speed`.
    *   If spread is against the wind, probability decreases (e.g., 0.5x).
4.  **Target Fuel Load**: Probability increases with higher `fuel_load` in the target cell.
5.  **Temperature & Humidity**:
    *   Higher temperature increases probability.
    *   Lower humidity increases probability.
6.  **Cap**: The final probability is capped (e.g., at 0.9 or 90%).

If `random.random() < spread_prob`, the target cell ignites (`fire_state` becomes `BURNING`, `ignition_time` is set).

### 3. Fire Aging and Burnout (`FireGrid._age_fires`)

*   Cells that are `BURNING` can naturally burn out.
*   Burnout time is determined by `fuel_load` (e.g., `cell.fuel_load * 2` hours).
*   If `current_time - ignition_time` exceeds this duration, the cell's state changes from `BURNING` to `BURNED`.

### 4. Fire Suppression (`FireGrid.apply_suppression`)

This simulates firefighting efforts:

*   Takes `suppression_points` as input (representing firefighting resources).
*   These points are distributed among all currently `BURNING` cells.
*   For each burning cell, a containment probability is calculated:
    *   Base probability increases with `points_per_cell`.
    *   **Terrain Difficulty**:
        *   Urban: Harder to contain (e.g., 0.6x probability).
        *   Valley: Easier access (e.g., 1.3x probability).
        *   Ridge: Difficult access (e.g., 0.8x probability).
*   If `random.random() < contain_prob`, the cell's state changes from `BURNING` to `CONTAINED`.

### 5. Advancing Operational Periods (`FireGrid.advance_operational_period`)

*   Increments the `operational_period` counter.
*   Generates new `WeatherConditions`.
*   Simulates passage of time by running the `spread_fire` logic multiple times (e.g., 3 times).

## Output and State Tracking

### Fire Statistics (`FireGrid.get_fire_statistics`)

Provides a summary of the fire's current state:

*   `fire_size_acres`: Total acres affected (burning + burned + contained cells * 10 acres/cell).
*   `containment_percent`: Percentage of (contained cells) / (burning + contained cells).
*   Counts of active, burned, and contained cells.
*   Current weather details and fire danger rating.
*   Current operational period and incident duration.

### Threat Assessment (`FireGrid.get_threat_assessment`)

*   Identifies `URBAN` cells.
*   Determines how many urban cells are currently burning or adjacent to burning cells (threatened).
*   Calculates a `threat_level` (LOW, MODERATE, HIGH, EXTREME) based on the ratio of threatened to total urban cells.
*   Estimates total and threatened structures (assuming a fixed number of structures per urban cell).
*   Recommends evacuation if urban cells are threatened.

## Simplifications and Assumptions

*   **Discrete Time Steps**: The simulation progresses in discrete steps (spread attempts, operational periods).
*   **Uniform Cell Size**: All cells represent a fixed area (10 acres).
*   **Abstracted Resources**: Suppression is handled via abstract `suppression_points` rather than simulating individual units.
*   **No Spotting**: Long-distance fire spotting is not explicitly modeled, though rapid spread in certain conditions can simulate similar effects.
*   **Internal Grid**: The fire grid itself is for internal simulation and not directly visualized to players, aligning with design principles focusing on command-level interaction.

This algorithm provides a balance between realistic fire behavior modeling and computational feasibility for a Discord bot application.
