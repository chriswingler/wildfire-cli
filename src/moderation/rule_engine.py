"""
Manages moderation rules defined in a YAML configuration file.

This module provides classes for representing moderation rules, actions,
and categories, and a RuleEngine class to load and access these rules.
"""
import yaml
import os
import dataclasses
import logging # Added for better error logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__) # For module-level logging

@dataclasses.dataclass
class RuleAction:
    """
    Represents a single action to be taken when a rule is violated.

    Attributes:
        type: The type of action (e.g., "warning", "timeout", "ban").
        params: Optional parameters for the action (e.g., duration for a timeout).
    """
    type: str
    params: Optional[Dict[str, Any]] = None

@dataclasses.dataclass
class RuleDefinition:
    """
    Defines a specific moderation rule.

    Attributes:
        enabled: Whether the rule is currently active.
        threshold: The confidence score or value threshold for this rule to trigger.
        actions: A list of RuleAction objects to be taken if the rule is violated.
        description: An optional human-readable description of the rule.
        severity_score: An integer score representing the severity of violating this rule.
    """
    enabled: bool
    threshold: float
    actions: List[RuleAction]
    description: Optional[str] = None
    severity_score: int = 0

@dataclasses.dataclass
class RuleCategory:
    """
    Represents a category of moderation rules.

    Attributes:
        name: The name of the rule category (e.g., "Spam Detection").
        rules: A dictionary mapping rule names to their RuleDefinition objects.
    """
    name: str
    rules: Dict[str, RuleDefinition]

class RuleEngine:
    """
    Loads and provides access to moderation rules from a YAML configuration file.
    """
    def __init__(self, config_path: Optional[str] = None) -> None:
        """
        Initializes the RuleEngine.

        Args:
            config_path: Optional path to the YAML configuration file.
                         If None, defaults to 'config/moderation_rules.yaml' relative
                         to the project root.
        """
        if config_path is None:
            # Assuming the script runs from a location where this relative path is valid.
            # For robustness, consider using absolute paths or a more reliable way to find the root.
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.config_path: str = os.path.join(base_dir, "..", "..", "config", "moderation_rules.yaml")
        else:
            self.config_path = config_path

        self.rule_categories: Dict[str, RuleCategory] = {}
        self.load_rules()

    def load_rules(self) -> None:
        """
        Loads moderation rules from the YAML file specified in `self.config_path`.

        Populates `self.rule_categories`. Handles FileNotFoundError and YAMLError
        by logging an error message.
        """
        try:
            with open(self.config_path, "r", encoding="utf-8") as f: # Added encoding
                config_data = yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Error: Configuration file not found at {self.config_path}")
            # Consider raising a custom exception or returning a status
            return
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration at {self.config_path}: {e}")
            # Consider raising a custom exception or returning a status
            return

        if not isinstance(config_data, dict) or "rule_categories" not in config_data:
            logger.error(f"Error: Invalid configuration format in {self.config_path}. 'rule_categories' key missing or not a dict.")
            return

        loaded_categories: Dict[str, RuleCategory] = {}
        for category_data in config_data.get("rule_categories", []):
            if not isinstance(category_data, dict) or "name" not in category_data or "rules" not in category_data:
                logger.warning(f"Skipping malformed category data in {self.config_path}: {category_data}")
                continue

            category_name = category_data["name"]
            rules_data = category_data["rules"]
            rules: Dict[str, RuleDefinition] = {}

            if not isinstance(rules_data, dict):
                logger.warning(f"Skipping malformed rules section for category '{category_name}' in {self.config_path}.")
                continue

            for rule_name, rule_details in rules_data.items():
                if not isinstance(rule_details, dict):
                    logger.warning(f"Skipping malformed rule '{rule_name}' in category '{category_name}'.")
                    continue
                try:
                    actions_data = rule_details.get("actions", [])
                    actions = [RuleAction(**action_data) for action_data in actions_data]

                    rules[rule_name] = RuleDefinition(
                        enabled=bool(rule_details.get("enabled", False)), # Explicit bool conversion
                        threshold=float(rule_details.get("threshold", 0.0)), # Explicit float conversion
                        actions=actions,
                        description=rule_details.get("description"),
                        severity_score=int(rule_details.get("severity_score", 0)), # Explicit int conversion
                    )
                except (TypeError, ValueError) as e:
                    logger.warning(f"Skipping rule '{rule_name}' in category '{category_name}' due to data error: {e}")

            if category_name in loaded_categories:
                 logger.warning(f"Duplicate category name '{category_name}' found. Overwriting previous definition.")
            loaded_categories[category_name] = RuleCategory(name=category_name, rules=rules)

        self.rule_categories = loaded_categories


    def get_rule(self, category_name: str, rule_name: str) -> Optional[RuleDefinition]:
        """
        Retrieves a specific rule definition.

        Args:
            category_name: The name of the category.
            rule_name: The name of the rule.

        Returns:
            The RuleDefinition object if found, else None.
        """
        category = self.rule_categories.get(category_name)
        if category:
            return category.rules.get(rule_name)
        return None

    def get_category_rules(self, category_name: str) -> Optional[RuleCategory]:
        """
        Retrieves all rules within a specific category.

        Args:
            category_name: The name of the category.

        Returns:
            The RuleCategory object if found, else None.
        """
        return self.rule_categories.get(category_name)

    def is_rule_enabled(self, category_name: str, rule_name: str) -> bool:
        """
        Checks if a specific rule is currently enabled.

        Args:
            category_name: The name of the category.
            rule_name: The name of the rule.

        Returns:
            True if the rule is enabled, False if disabled, not found, or category not found.
        """
        rule = self.get_rule(category_name, rule_name)
        return rule.enabled if rule else False
