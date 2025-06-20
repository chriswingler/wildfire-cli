import unittest
import yaml
import os
from pathlib import Path
from src.moderation.rule_engine import RuleEngine, RuleDefinition, RuleAction, RuleCategory

class TestRuleEngine(unittest.TestCase):
    def setUp(self):
        self.test_config_dir = Path("tests/config_for_tests")
        self.test_config_dir.mkdir(parents=True, exist_ok=True)
        self.test_yaml_path = self.test_config_dir / "test_moderation_rules.yaml"

        test_rules_content = {
            "rule_categories": [
                {
                    "name": "Test Spam",
                    "rules": {
                        "test_spam_rule": {
                            "description": "Test spam rule",
                            "enabled": True,
                            "threshold": 0.8,
                            "severity_score": 5,
                            "actions": [{"type": "warning"}],
                        }
                    },
                },
                {
                    "name": "Test Toxicity",
                    "rules": {
                        "test_toxic_rule": {
                            "description": "Test toxic rule",
                            "enabled": False,
                            "threshold": 0.9,
                            "severity_score": 10,
                            "actions": [{"type": "delete_message"}],
                        }
                    },
                },
            ]
        }
        with open(self.test_yaml_path, 'w') as f:
            yaml.dump(test_rules_content, f)

    def tearDown(self):
        if self.test_yaml_path.exists():
            self.test_yaml_path.unlink()
        # Only remove if empty - though setUp ensures it's created, other tests might use it.
        # For this specific test, it should be empty after its own YAML is deleted.
        if self.test_config_dir.exists() and not any(self.test_config_dir.iterdir()):
            # Check for .keep file if that's standard practice
            keep_file = self.test_config_dir / ".keep"
            if keep_file.exists() and len(list(self.test_config_dir.iterdir())) == 1:
                 pass # Only .keep file exists, can be removed if desired or left
            elif not any(self.test_config_dir.iterdir()): # Truly empty
                self.test_config_dir.rmdir()


    def test_load_rules(self):
        rule_engine = RuleEngine(config_path=str(self.test_yaml_path))
        self.assertEqual(len(rule_engine.rule_categories), 2)
        self.assertIn("Test Spam", rule_engine.rule_categories)

        spam_category = rule_engine.rule_categories["Test Spam"]
        self.assertIsInstance(spam_category, RuleCategory)
        spam_rules = spam_category.rules
        self.assertIn("test_spam_rule", spam_rules)

        spam_rule_def = spam_rules["test_spam_rule"]
        self.assertIsInstance(spam_rule_def, RuleDefinition)
        self.assertTrue(spam_rule_def.enabled)
        self.assertEqual(spam_rule_def.threshold, 0.8)
        self.assertEqual(spam_rule_def.severity_score, 5)
        self.assertEqual(len(spam_rule_def.actions), 1)
        self.assertIsInstance(spam_rule_def.actions[0], RuleAction)
        self.assertEqual(spam_rule_def.actions[0].type, "warning")

    def test_get_rule(self):
        rule_engine = RuleEngine(config_path=str(self.test_yaml_path))
        self.assertIsNotNone(rule_engine.get_rule("Test Spam", "test_spam_rule"))
        self.assertIsNone(rule_engine.get_rule("NonExistentCategory", "test_spam_rule"))
        self.assertIsNone(rule_engine.get_rule("Test Spam", "non_existent_rule"))

    def test_is_rule_enabled(self):
        rule_engine = RuleEngine(config_path=str(self.test_yaml_path))
        self.assertTrue(rule_engine.is_rule_enabled("Test Spam", "test_spam_rule"))
        self.assertFalse(rule_engine.is_rule_enabled("Test Toxicity", "test_toxic_rule"))
        self.assertFalse(rule_engine.is_rule_enabled("NonExistentCategory", "test_spam_rule"))

if __name__ == '__main__':
    unittest.main()
