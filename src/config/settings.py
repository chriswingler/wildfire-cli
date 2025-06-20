import yaml
import os
from dataclasses import dataclass, field
from typing import Dict, Any, Union
from pathlib import Path

# Path for the analytics database
ANALYTICS_DB_PATH = "./data/analytics.db"

@dataclass
class ResourceCosts:
    hand_crews: int
    engines: int
    dozers: int
    air_tankers: int

@dataclass
class GameEconomy:
    starting_budget: int
    bonus_amount: int
    resource_costs: ResourceCosts

@dataclass
class FireSizeRange: # Added this dataclass for proper typing
    min_acres: int
    max_acres: int

@dataclass
class GameProgression:
    button_timeout_seconds: int
    auto_progression_seconds: int
    fire_size_range: FireSizeRange # Updated type

@dataclass
class EffectivenessMultipliers:
    terrain_multipliers: Dict[str, float]
    weather_impact: Dict[str, float]
    resource_effectiveness: Dict[str, float]

@dataclass
class GameThresholds: # Added this dataclass for proper typing
    critical_failure_acres: int
    containment_success_percent: int
    resource_effectiveness_base: float # Changed to float based on YAML

@dataclass
class GameConfig:
    economy: GameEconomy
    progression: GameProgression
    thresholds: GameThresholds # Updated type
    effectiveness: EffectivenessMultipliers

@dataclass
class DiscordEmbedColorCodes: # Added for discord config section
    success: int
    warning: int
    danger: int
    info: int

@dataclass
class DiscordConfig: # Added for discord config section
    interaction_timeout: int
    embed_color_codes: DiscordEmbedColorCodes

@dataclass
class AppConfig: # Main config object holding game and discord configs
    game: GameConfig
    discord: DiscordConfig


class ConfigManager:
    def __init__(self):
        self.config: AppConfig = None # Changed to AppConfig
        self.environment = os.getenv('WILDFIRE_ENV', 'production')
        self._load_config() # Load config during initialization

    def _load_config(self): # Renamed to _load_config for internal use
        """Load configuration based on environment."""
        config_dir = Path(__file__).resolve().parent.parent.parent / 'config'

        base_config_path = config_dir / 'game_balance.yaml'
        if not base_config_path.exists():
            raise FileNotFoundError(f"Base configuration file not found at {base_config_path}")
        with open(base_config_path, 'r') as f:
            base_config_data = yaml.safe_load(f)

        env_config_path = config_dir / f'{self.environment}.yaml'
        if self.environment != 'production' and env_config_path.exists():
            with open(env_config_path, 'r') as f:
                env_config_data = yaml.safe_load(f)
                if env_config_data:
                    base_config_data = self._merge_configs(base_config_data, env_config_data)
        elif self.environment == 'production':
            prod_env_config_path = config_dir / 'production.yaml'
            if prod_env_config_path.exists():
                 with open(prod_env_config_path, 'r') as f:
                    env_config_data = yaml.safe_load(f)
                    if env_config_data:
                        base_config_data = self._merge_configs(base_config_data, env_config_data)

        self.config = self._dict_to_app_config(base_config_data)

    def _merge_configs(self, base: dict, override: dict) -> dict:
        """Deep merge configuration dictionaries."""
        for key, value in override.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                base[key] = self._merge_configs(base[key], value)
            else:
                base[key] = value
        return base

    def _dict_to_app_config(self, config_dict: dict) -> AppConfig:
        """Convert configuration dictionary to typed AppConfig dataclass."""
        game_config_dict = config_dict['game']

        resource_costs = ResourceCosts(**game_config_dict['economy']['resource_costs'])
        economy = GameEconomy(
            starting_budget=game_config_dict['economy']['starting_budget'],
            bonus_amount=game_config_dict['economy']['bonus_amount'],
            resource_costs=resource_costs
        )

        fire_size_range_data = game_config_dict['progression']['fire_size_range']
        fire_size_range = FireSizeRange(**fire_size_range_data)
        progression = GameProgression(
            button_timeout_seconds=game_config_dict['progression']['button_timeout_seconds'],
            auto_progression_seconds=game_config_dict['progression']['auto_progression_seconds'],
            fire_size_range=fire_size_range
        )

        thresholds_data = game_config_dict['thresholds']
        thresholds = GameThresholds(**thresholds_data)

        effectiveness_data = game_config_dict['effectiveness']
        effectiveness = EffectivenessMultipliers(**effectiveness_data)

        game_config = GameConfig(
            economy=economy,
            progression=progression,
            thresholds=thresholds,
            effectiveness=effectiveness
        )

        discord_config_dict = config_dict.get('discord', {})
        embed_colors_data = discord_config_dict.get('embed_color_codes', {})
        embed_color_codes = DiscordEmbedColorCodes(**embed_colors_data)

        discord_config = DiscordConfig(
            interaction_timeout=discord_config_dict.get('interaction_timeout', 300),
            embed_color_codes=embed_color_codes
        )

        return AppConfig(game=game_config, discord=discord_config)

try:
    config_manager = ConfigManager()
    config = config_manager.config
except FileNotFoundError as e:
    print(f"CONFIG ERROR: {e}. Please ensure 'config/game_balance.yaml' exists and paths are correct.")
    raise
except Exception as e:
    print(f"CONFIG ERROR: Failed to load or parse configuration: {e}")
    raise
