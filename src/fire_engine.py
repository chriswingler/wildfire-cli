"""
@file fire_engine.py
@brief Core wildfire simulation engine with cellular automata
@details Implements realistic fire spread, terrain effects, and weather conditions
"""

import random
import time
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json


class TerrainType(Enum):
    """Terrain types affecting fire behavior."""
    FOREST = "forest"
    GRASS = "grass" 
    URBAN = "urban"
    RIDGE = "ridge"
    VALLEY = "valley"


class FireState(Enum):
    """Fire states for cellular automata."""
    EMPTY = "empty"
    BURNING = "burning"
    BURNED = "burned"
    CONTAINED = "contained"


class WeatherConditions:
    """Weather conditions affecting fire behavior."""
    
    def __init__(self):
        self.wind_direction = random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"])
        self.wind_speed = random.randint(5, 25)  # mph
        self.temperature = random.randint(75, 105)  # fahrenheit
        self.humidity = random.randint(10, 60)  # percent
        self.forecast_reliability = random.choice(["high", "moderate", "low"])
        
    def get_fire_danger_rating(self):
        """Calculate fire danger based on weather conditions."""
        danger_score = 0
        
        # Wind speed factor
        if self.wind_speed > 20:
            danger_score += 3
        elif self.wind_speed > 15:
            danger_score += 2
        else:
            danger_score += 1
            
        # Temperature factor
        if self.temperature > 95:
            danger_score += 3
        elif self.temperature > 85:
            danger_score += 2
        else:
            danger_score += 1
            
        # Humidity factor (inverted - lower humidity = higher danger)
        if self.humidity < 20:
            danger_score += 3
        elif self.humidity < 40:
            danger_score += 2
        else:
            danger_score += 1
            
        # Convert to rating
        if danger_score >= 8:
            return "EXTREME"
        elif danger_score >= 6:
            return "HIGH"
        elif danger_score >= 4:
            return "MODERATE"
        else:
            return "LOW"


class FireCell:
    """Individual cell in the fire grid."""
    
    def __init__(self, terrain: TerrainType, x: int, y: int):
        self.terrain = terrain
        self.fire_state = FireState.EMPTY
        self.ignition_time = None
        self.contained_time = None
        self.x = x
        self.y = y
        self.fuel_load = self._calculate_fuel_load()
        self.burn_intensity = 0
        
    def _calculate_fuel_load(self):
        """Calculate fuel load based on terrain type."""
        fuel_loads = {
            TerrainType.GRASS: random.randint(1, 3),
            TerrainType.FOREST: random.randint(4, 8), 
            TerrainType.URBAN: random.randint(6, 10),
            TerrainType.RIDGE: random.randint(2, 5),
            TerrainType.VALLEY: random.randint(3, 6)
        }
        return fuel_loads.get(self.terrain, 3)
        
    def ignite(self):
        """Set cell on fire."""
        if self.fire_state == FireState.EMPTY:
            self.fire_state = FireState.BURNING
            self.ignition_time = datetime.now()
            self.burn_intensity = self.fuel_load
            
    def burn_out(self):
        """Cell burns out naturally."""
        if self.fire_state == FireState.BURNING:
            self.fire_state = FireState.BURNED
            self.burn_intensity = 0
            
    def contain(self):
        """Fire contained by suppression efforts."""
        if self.fire_state == FireState.BURNING:
            self.fire_state = FireState.CONTAINED
            self.contained_time = datetime.now()
            self.burn_intensity = 0


class FireGrid:
    """
    @brief Core fire simulation using cellular automata
    @details Internal grid simulation - never displayed visually per design principles
    """
    
    def __init__(self, size: int = 8):
        """
        Initializes the FireGrid.

        :param size: The dimension of the square grid (e.g., 8 for an 8x8 grid).
        :type size: int
        """
        self.size = size
        self.grid: List[List[FireCell]] = []
        self.weather = WeatherConditions()
        self.operational_period = 1
        self.incident_start_time = datetime.now()
        self.total_acres = size * size * 10  # Each cell represents 10 acres.
        self._initialize_grid()
        
    def _initialize_grid(self):
        """
        Initializes the grid with FireCell objects, assigning terrain types
        based on predefined weights.
        """
        # terrain_weights define the probability distribution for different terrain types.
        # For example, FOREST has a 40% chance, GRASS 30%, etc.
        # These weights are used to create a list from which random.choice picks.
        terrain_weights = {
            TerrainType.FOREST: 0.4,
            TerrainType.GRASS: 0.3,
            TerrainType.URBAN: 0.1, 
            TerrainType.RIDGE: 0.1,
            TerrainType.VALLEY: 0.1
        }
        
        terrain_choices = []
        for terrain, weight in terrain_weights.items():
            terrain_choices.extend([terrain] * int(weight * 100))
            
        for y in range(self.size):
            row = []
            for x in range(self.size):
                terrain = random.choice(terrain_choices)
                cell = FireCell(terrain, x, y)
                row.append(cell)
            self.grid.append(row)
    
    def start_fire(self, intensity: str = "moderate"):
        """Start initial fire at random location."""
        start_x = random.randint(1, self.size - 2)
        start_y = random.randint(1, self.size - 2)
        
        self.grid[start_y][start_x].ignite()
        
        # Start additional cells based on intensity
        if intensity == "high":
            additional_cells = 3
        elif intensity == "low":
            additional_cells = 1
        else:
            additional_cells = 2
            
        for _ in range(additional_cells):
            adj_x = start_x + random.choice([-1, 0, 1])
            adj_y = start_y + random.choice([-1, 0, 1])
            if 0 <= adj_x < self.size and 0 <= adj_y < self.size:
                self.grid[adj_y][adj_x].ignite()
    
    def spread_fire(self):
        """Spread fire to adjacent cells based on conditions."""
        new_fires = []
        
        for y in range(self.size):
            for x in range(self.size):
                cell = self.grid[y][x]
                
                if cell.fire_state == FireState.BURNING:
                    # Check adjacent cells for spread
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                                
                            new_x, new_y = x + dx, y + dy
                            if 0 <= new_x < self.size and 0 <= new_y < self.size:
                                adjacent_cell = self.grid[new_y][new_x]
                                
                                if adjacent_cell.fire_state == FireState.EMPTY:
                                    spread_prob = self._calculate_spread_probability(
                                        cell, adjacent_cell, dx, dy
                                    )
                                    if random.random() < spread_prob:
                                        new_fires.append((new_x, new_y))
        
        # Apply new fires
        for x, y in new_fires:
            self.grid[y][x].ignite()
            
        # Age existing fires
        self._age_fires()
    
    def _calculate_spread_probability(self, source: FireCell, target: FireCell, 
                                    dx: int, dy: int) -> float:
        """
        Calculate probability of fire spreading from a source cell to a target adjacent cell.

        The probability is influenced by several factors:
        - Base probability: A starting chance of spread.
        - Target terrain: Different terrains have multipliers (e.g., grass spreads faster).
        - Wind: Spreading with wind increases probability, against wind decreases it.
        - Target fuel load: Higher fuel load in the target cell increases probability.
        - Temperature: Higher temperatures increase probability.
        - Humidity: Lower humidity increases probability.
        The final probability is a combination of these factors and is capped.

        :param source: The FireCell object that is currently burning.
        :type source: FireCell
        :param target: The FireCell object that is a candidate for ignition.
        :type target: FireCell
        :param dx: The difference in x-coordinate from source to target (e.g., -1, 0, 1).
        :type dx: int
        :param dy: The difference in y-coordinate from source to target (e.g., -1, 0, 1).
        :type dy: int
        :return: The calculated spread probability (0.0 to 0.9).
        :rtype: float
        """
        base_prob = 0.3  # Initial base probability for spread.
        
        # Terrain effects: Multipliers based on the target cell's terrain type.
        # Grass burns easily, Urban areas might be more resistant initially or channel fire differently.
        terrain_multipliers = {
            TerrainType.GRASS: 1.5,  # Fast spread due to fine fuels.
            TerrainType.FOREST: 1.0,  # Normal spread rate.
            TerrainType.URBAN: 0.8,   # Slower initial spread, but implies high value and potential for intense burning.
            TerrainType.RIDGE: 1.2,   # Fire tends to spread faster uphill.
            TerrainType.VALLEY: 0.7   # Valleys can act as barriers or channel wind, here simplified to slower.
        }
        prob = base_prob * terrain_multipliers.get(target.terrain, 1.0)
        
        # Wind effects: Wind direction and speed significantly impact spread.
        # Spread is more likely if aligned with wind direction, less likely against it.
        wind_directions = {
            "N": (0, -1), "NE": (1, -1), "E": (1, 0), "SE": (1, 1),
            "S": (0, 1), "SW": (-1, 1), "W": (-1, 0), "NW": (-1, -1)
        }
        wind_dx, wind_dy = wind_directions[self.weather.wind_direction]
        
        if dx == wind_dx and dy == wind_dy:  # Spreading in the same direction as the wind.
            prob *= (1 + self.weather.wind_speed / 25.0)  # Increase prob based on wind speed (max speed 25mph).
        elif dx == -wind_dx and dy == -wind_dy:  # Spreading directly against the wind.
            prob *= 0.5  # Significantly reduce probability.
            
        # Fuel load effect: Higher fuel load in the target cell means more material to burn.
        # Normalized by a factor (e.g., 5.0) to scale its impact.
        prob *= (target.fuel_load / 5.0)
        
        # Temperature and humidity effects: Higher temperature and lower humidity favor fire spread.
        # Normalized by 100 to represent them as factors.
        prob *= (self.weather.temperature / 100.0)  # Higher temp increases prob.
        prob *= (1.0 - self.weather.humidity / 100.0)  # Lower humidity increases prob.
        
        # Final probability is capped to prevent certainty and keep some randomness.
        return min(prob, 0.9)
    
    def _age_fires(self):
        """
        Ages existing fires. If a fire has been burning for a duration determined
        by its fuel_load, it transitions to the BURNED state (natural burnout).
        """
        for y in range(self.size):
            for x in range(self.size):
                cell = self.grid[y][x]
                
                if cell.fire_state == FireState.BURNING and cell.ignition_time:
                    burn_time = datetime.now() - cell.ignition_time
                    
                    # Natural burnout condition:
                    # Burnout time is proportional to fuel_load.
                    # Here, each unit of fuel_load is assumed to burn for approx. 2 hours.
                    burnout_hours = cell.fuel_load * 2
                    if burn_time.total_seconds() / 3600 > burnout_hours:
                        cell.burn_out()
    
    def apply_suppression(self, suppression_points: int):
        """
        Applies suppression efforts to currently burning cells.

        Suppression points (representing firefighting resources) are distributed
        among all burning cells. The probability of containing a cell depends
        on the points allocated to it and the terrain difficulty.

        :param suppression_points: Total suppression points available for this turn.
        :type suppression_points: int
        """
        burning_cells = []
        for y in range(self.size):
            for x in range(self.size):
                cell = self.grid[y][x]
                if cell.fire_state == FireState.BURNING:
                    burning_cells.append(cell)
        
        if not burning_cells:
            return # No active fires to suppress.
            
        # Distribute suppression effort evenly among all burning cells.
        # Each burning cell gets at least 1 point if points are available.
        points_per_cell = max(1, suppression_points // len(burning_cells))
        
        for cell in burning_cells:
            # Base containment probability increases with more points allocated to the cell.
            # Capped at 0.8 to ensure containment isn't guaranteed solely by points.
            contain_prob = min(0.8, points_per_cell * 0.1)
            
            # Terrain difficulty factors modify containment probability.
            # Some terrains are harder to operate in or have more resilient structures.
            if cell.terrain == TerrainType.URBAN:
                contain_prob *= 0.6  # Urban environments can be complex and challenging for suppression.
            elif cell.terrain == TerrainType.VALLEY:
                contain_prob *= 1.3  # Valleys might offer better access or tactical advantages.
            elif cell.terrain == TerrainType.RIDGE:
                contain_prob *= 0.8  # Ridges can be difficult to access and work on.
                
            if random.random() < contain_prob:
                cell.contain() # Cell is successfully contained.
    
    def get_fire_statistics(self) -> Dict:
        """
        Calculates and returns current statistics about the fire situation on the grid.

        This includes the number of acres burned/burning/contained, overall containment percentage,
        cell counts by state, weather information, operational period, and incident duration.

        :return: A dictionary containing various fire statistics.
        :rtype: Dict
        """
        burning_count = 0
        burned_count = 0
        contained_count = 0
        total_cells = self.size * self.size
        
        for y in range(self.size):
            for x in range(self.size):
                cell = self.grid[y][x]
                if cell.fire_state == FireState.BURNING:
                    burning_count += 1
                elif cell.fire_state == FireState.BURNED:
                    burned_count += 1
                elif cell.fire_state == FireState.CONTAINED:
                    contained_count += 1
        
        fire_size_acres = (burning_count + burned_count + contained_count) * 10
        containment_percent = int((contained_count / max(1, burning_count + contained_count)) * 100)
        
        return {
            "fire_size_acres": fire_size_acres,
            "containment_percent": containment_percent,
            "active_cells": burning_count,
            "burned_cells": burned_count,
            "contained_cells": contained_count,
            "total_cells": total_cells,
            "weather": {
                "wind_direction": self.weather.wind_direction,
                "wind_speed": self.weather.wind_speed,
                "temperature": self.weather.temperature,
                "humidity": self.weather.humidity,
                "fire_danger": self.weather.get_fire_danger_rating()
            },
            "operational_period": self.operational_period,
            "incident_duration": str(datetime.now() - self.incident_start_time).split('.')[0]
        }
    
    def advance_operational_period(self):
        """Advance to next operational period."""
        self.operational_period += 1
        
        # Update weather conditions
        self.weather = WeatherConditions()
        
        # Spread fire multiple times to simulate time passage
        for _ in range(3):
            self.spread_fire()
    
    def is_contained(self) -> bool:
        """Check if fire is fully contained."""
        for y in range(self.size):
            for x in range(self.size):
                if self.grid[y][x].fire_state == FireState.BURNING:
                    return False
        return True
    
    def get_threat_assessment(self) -> Dict:
        """Assess threats to structures and values at risk."""
        urban_cells = 0
        threatened_urban = 0
        
        for y in range(self.size):
            for x in range(self.size):
                cell = self.grid[y][x]
                if cell.terrain == TerrainType.URBAN:
                    urban_cells += 1
                    
                    # Check if threatened (burning or adjacent to burning)
                    if cell.fire_state == FireState.BURNING:
                        threatened_urban += 1
                    else:
                        # Check adjacent cells
                        for dy in [-1, 0, 1]:
                            for dx in [-1, 0, 1]:
                                if dx == 0 and dy == 0:
                                    continue
                                adj_x, adj_y = x + dx, y + dy
                                if 0 <= adj_x < self.size and 0 <= adj_y < self.size:
                                    if self.grid[adj_y][adj_x].fire_state == FireState.BURNING:
                                        threatened_urban += 1
                                        break
                            else:
                                continue
                            break
        
        threat_level = "LOW"
        if threatened_urban > 0:
            threat_ratio = threatened_urban / max(1, urban_cells)
            if threat_ratio > 0.5:
                threat_level = "EXTREME"
            elif threat_ratio > 0.25:
                threat_level = "HIGH"
            else:
                threat_level = "MODERATE"
        
        return {
            "threat_level": threat_level,
            "total_structures": urban_cells * 25,  # Assume 25 structures per urban cell
            "threatened_structures": threatened_urban * 25,
            "evacuation_recommended": threatened_urban > 0
        }