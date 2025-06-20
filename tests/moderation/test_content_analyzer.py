import unittest
import asyncio
from src.moderation.rule_engine import RuleEngine, RuleDefinition, RuleAction, RuleCategory
from src.moderation.content_analyzer import ContentAnalyzer, AnalysisResult

class TestContentAnalyzer(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self): # Changed from setUp to asyncSetUp for consistency with IsolatedAsyncioTestCase
        # Mock RuleEngine to avoid actual file loading
        self.rule_engine = RuleEngine(config_path=None)

        self.spam_action = RuleAction(type='warning', params={"message": "Spam detected"})
        self.spam_rule = RuleDefinition(enabled=True, threshold=0.8, severity_score=5, actions=[self.spam_action], description='Spam rule')

        self.toxic_action = RuleAction(type='delete_message')
        self.toxic_rule = RuleDefinition(enabled=True, threshold=0.9, severity_score=10, actions=[self.toxic_action], description='Toxic rule')

        self.harassment_action = RuleAction(type='timeout', params={"duration_seconds": 300})
        self.harassment_rule = RuleDefinition(enabled=True, threshold=0.85, severity_score=8, actions=[self.harassment_action], description='Harassment rule')

        # Directly set the rule_categories attribute instead of calling load_rules
        self.rule_engine.rule_categories = {
            "Spam Detection": RuleCategory(name="Spam Detection", rules={"repeated_text": self.spam_rule}),
            "Toxicity Filter": RuleCategory(name="Toxicity Filter", rules={"severe_toxicity": self.toxic_rule}),
            "Harassment": RuleCategory(name="Harassment", rules={"targeted_harassment": self.harassment_rule})
        }

        self.content_analyzer = ContentAnalyzer(self.rule_engine)
        # For spam check, set the previous message directly for predictable testing
        self.content_analyzer.previous_message_for_spam_check = "spam example"

    async def test_analyze_spam(self):
        # Pass the specific rule definition that ContentAnalyzer expects
        relevant_spam_rule_tuple = ("Spam Detection", "repeated_text", self.spam_rule)
        results = await self.content_analyzer.analyze_content(
            message_content="spam example",
            guild_id="guild1",
            user_id="user1",
            relevant_rules=[relevant_spam_rule_tuple]
        )
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], AnalysisResult)
        self.assertEqual(results[0].violated_rule_category, "Spam Detection")
        self.assertEqual(results[0].violated_rule_name, "repeated_text")
        self.assertEqual(results[0].severity, 5)
        self.assertGreaterEqual(results[0].confidence, 0.8) # Should meet or exceed threshold
        self.assertEqual(results[0].matched_content, "spam example")

    async def test_analyze_toxicity(self):
        relevant_toxic_rule_tuple = ("Toxicity Filter", "severe_toxicity", self.toxic_rule)
        results = await self.content_analyzer.analyze_content(
            message_content="some extreme_toxic_word here",
            guild_id="guild1",
            user_id="user1",
            relevant_rules=[relevant_toxic_rule_tuple]
        )
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], AnalysisResult)
        self.assertEqual(results[0].violated_rule_category, "Toxicity Filter")
        self.assertEqual(results[0].violated_rule_name, "severe_toxicity")
        self.assertEqual(results[0].severity, 10)
        self.assertGreaterEqual(results[0].confidence, 0.9)
        self.assertEqual(results[0].matched_content, "extreme_toxic_word")

    async def test_analyze_harassment(self):
        relevant_harassment_rule_tuple = ("Harassment", "targeted_harassment", self.harassment_rule)
        results = await self.content_analyzer.analyze_content(
            message_content="This is a harassing_phrase @someuser about something.",
            guild_id="guild1",
            user_id="user1",
            relevant_rules=[relevant_harassment_rule_tuple]
        )
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], AnalysisResult)
        self.assertEqual(results[0].violated_rule_category, "Harassment")
        self.assertEqual(results[0].violated_rule_name, "targeted_harassment")
        self.assertEqual(results[0].severity, 8)
        self.assertGreaterEqual(results[0].confidence, 0.85)
        self.assertTrue("harassing_phrase @" in results[0].matched_content if results[0].matched_content else False)

    async def test_analyze_no_violation(self):
        relevant_spam_rule_tuple = ("Spam Detection", "repeated_text", self.spam_rule)
        results = await self.content_analyzer.analyze_content(
            message_content="a perfectly normal message",
            guild_id="guild1",
            user_id="user1",
            relevant_rules=[relevant_spam_rule_tuple]
        )
        self.assertEqual(len(results), 0)

    async def test_analyze_multiple_rules_one_violation(self):
        relevant_rules = [
            ("Spam Detection", "repeated_text", self.spam_rule),
            ("Toxicity Filter", "severe_toxicity", self.toxic_rule)
        ]
        results = await self.content_analyzer.analyze_content(
            message_content="spam example", # This will trigger spam
            guild_id="guild1",
            user_id="user1",
            relevant_rules=relevant_rules
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].violated_rule_category, "Spam Detection")

    async def test_analyze_rule_disabled(self):
        disabled_rule = RuleDefinition(enabled=False, threshold=0.8, severity_score=5, actions=[self.spam_action])
        relevant_rules = [("Spam Detection", "repeated_text", disabled_rule)]
        results = await self.content_analyzer.analyze_content(
            message_content="spam example",
            guild_id="guild1",
            user_id="user1",
            relevant_rules=relevant_rules
        )
        self.assertEqual(len(results), 0)

if __name__ == '__main__':
    unittest.main()
