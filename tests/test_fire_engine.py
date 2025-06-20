import pytest
from src.fire_engine import FireGrid, FireState, TerrainType

def test_fire_grid_initialization():
    grid = FireGrid(size=10)
    assert grid.size == 10
    assert len(grid.grid) == 10
    assert len(grid.grid[0]) == 10
    for row in grid.grid:
        for cell in row:
            assert cell.fire_state == FireState.EMPTY
            assert isinstance(cell.terrain, TerrainType)

def test_start_fire():
    grid = FireGrid(size=10)
    grid.start_fire(intensity="low")

    burning_cells = 0
    for y in range(grid.size):
        for x in range(grid.size):
            if grid.grid[y][x].fire_state == FireState.BURNING:
                burning_cells += 1

    # Check that at least one cell is burning
    # The exact number can vary due to randomness in start_fire's additional cells
    assert burning_cells >= 1

def test_weather_initialization():
    grid = FireGrid(size=10)
    assert grid.weather is not None
    assert grid.weather.wind_speed >= 5 and grid.weather.wind_speed <= 25
    assert grid.weather.temperature >= 75 and grid.weather.temperature <= 105
    assert grid.weather.humidity >= 10 and grid.weather.humidity <= 60
    assert grid.weather.forecast_reliability in ["high", "moderate", "low"]

def test_get_fire_statistics():
    grid = FireGrid(size=8) # Default size
    stats = grid.get_fire_statistics()

    assert stats["total_cells"] == 64
    assert stats["fire_size_acres"] == 0 # No fire started
    assert stats["containment_percent"] == 0
    assert stats["active_cells"] == 0

    grid.start_fire(intensity="low")
    stats_after_fire = grid.get_fire_statistics()
    assert stats_after_fire["fire_size_acres"] > 0
    assert stats_after_fire["active_cells"] > 0
