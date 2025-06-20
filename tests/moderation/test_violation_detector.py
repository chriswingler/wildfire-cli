import unittest
import asyncio
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock # AsyncMock for async methods

# Adjust imports based on actual project structure if src. is not how it's resolved
from src.moderation.violation_detector import ViolationDetector
from src.moderation.rule_engine import RuleEngine, RuleDefinition, RuleAction, RuleCategory
from src.moderation.content_analyzer import ContentAnalyzer, AnalysisResult
from src.database.moderation_db import ModerationDB

class TestViolationDetector(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self): # Changed to asyncSetUp
        self.mock_rule_engine = MagicMock(spec=RuleEngine)
        self.mock_content_analyzer = MagicMock(spec=ContentAnalyzer)
        # ModerationDB methods are async, so use AsyncMock for them if mocking individual methods
        # If just passing the spec, MagicMock is fine, but calls to its methods need to be AsyncMock
        self.mock_moderation_db = MagicMock(spec=ModerationDB)

        # Ensure async methods of mocks are AsyncMock
        self.mock_content_analyzer.analyze_content = AsyncMock()
        self.mock_moderation_db.log_violation = AsyncMock()
        self.mock_moderation_db.update_user_violation_summary = AsyncMock()
        self.mock_moderation_db.get_user_violation_status = AsyncMock()

        self.detector = ViolationDetector(
            self.mock_rule_engine,
            self.mock_content_analyzer,
            self.mock_moderation_db
        )

    async def test_no_violation_found_no_rules(self):
        self.mock_rule_engine.rule_categories = {} # No rules defined
        # analyze_content shouldn't even be called if there are no relevant_rules

        actions = await self.detector.check_message_for_violations("hello", "g1", "u1", "m1", "c1")

        self.assertEqual(len(actions), 0)
        self.mock_content_analyzer.analyze_content.assert_not_called() # Important check
        self.mock_moderation_db.log_violation.assert_not_called()

    async def test_no_violation_found_analyzer_returns_empty(self):
        # Setup a dummy enabled rule, otherwise analyze_content won't be called
        enabled_action = RuleAction(type="warning")
        enabled_rule_def = RuleDefinition(enabled=True, threshold=0.8, severity_score=5, actions=[enabled_action])
        mock_category = MagicMock(spec=RuleCategory)
        mock_category.rules = {"EnabledRule": enabled_rule_def}
        mock_category.name = "TestCatEnabled"
        self.mock_rule_engine.rule_categories = {"TestCatEnabled": mock_category}

        self.mock_content_analyzer.analyze_content.return_value = [] # Analyzer finds nothing

        actions = await self.detector.check_message_for_violations("hello", "g1", "u1", "m1", "c1")

        self.assertEqual(len(actions), 0)
        self.mock_content_analyzer.analyze_content.assert_called_once()
        self.mock_moderation_db.log_violation.assert_not_called()


    async def test_simple_violation_first_action(self):
        test_action = RuleAction(type="warning", params={"message": "test"})
        test_rule_def = RuleDefinition(enabled=True, threshold=0.8, severity_score=5, actions=[test_action], description="Test")

        # Rule engine setup for the detector
        mock_category = MagicMock(spec=RuleCategory)
        mock_category.rules = {"TestRule": test_rule_def}
        mock_category.name = "TestCat"
        self.mock_rule_engine.rule_categories = {"TestCat": mock_category}
        # Also need get_rule to return the definition for action selection
        self.mock_rule_engine.get_rule.return_value = test_rule_def

        analysis_res = AnalysisResult(
            violated_rule_category="TestCat",
            violated_rule_name="TestRule",
            confidence=0.9,
            severity=5,
            message="bad word",
            matched_content="bad word"
        )
        self.mock_content_analyzer.analyze_content.return_value = [analysis_res]
        self.mock_moderation_db.get_user_violation_status.return_value = {"warning_level": 0, "violation_count": 0, "last_violation": None}

        actions = await self.detector.check_message_for_violations("bad word", "g1", "u1", "m1", "c1")

        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].type, "warning")
        self.assertEqual(actions[0].params["message"], "test")

        self.mock_content_analyzer.analyze_content.assert_called_once()
        self.mock_moderation_db.log_violation.assert_called_once_with(
            guild_id="g1",
            user_id="u1",
            message_id="m1",
            channel_id="c1",
            violation_type="TestCat",
            rule_name="TestRule",
            severity=5,
            action_taken="warning ({'message': 'test'})", # Check how action string is formatted
            matched_content="bad word",
            duration_seconds=None # Assuming not set for warning
        )
        self.mock_moderation_db.update_user_violation_summary.assert_called_once()
        # Check args for update_user_violation_summary
        args, _ = self.mock_moderation_db.update_user_violation_summary.call_args
        self.assertEqual(args[0], "g1") # guild_id
        self.assertEqual(args[1], "u1") # user_id
        self.assertEqual(args[2], 5)    # severity_increment
        self.assertIsInstance(args[3], datetime) # violation_timestamp

    async def test_violation_escalated_action(self):
        action1 = RuleAction(type="warning", params={"message": "first warning"})
        action2 = RuleAction(type="timeout", params={"duration_seconds": 300, "reason": "escalated"})
        test_rule_def = RuleDefinition(enabled=True, threshold=0.8, severity_score=7, actions=[action1, action2], description="Escalation Test")

        mock_category = MagicMock(spec=RuleCategory)
        mock_category.rules = {"EscalationRule": test_rule_def}
        mock_category.name = "EscalationCat"
        self.mock_rule_engine.rule_categories = {"EscalationCat": mock_category}
        self.mock_rule_engine.get_rule.return_value = test_rule_def # Important for action fetching

        analysis_res = AnalysisResult(
            violated_rule_category="EscalationCat",
            violated_rule_name="EscalationRule",
            confidence=0.95,
            severity=7,
            message="very bad word",
            matched_content="very bad word"
        )
        self.mock_content_analyzer.analyze_content.return_value = [analysis_res]
        # Simulate user having a warning_level that triggers escalation
        self.mock_moderation_db.get_user_violation_status.return_value = {"warning_level": 2, "violation_count": 1, "last_violation": datetime.now()}

        actions = await self.detector.check_message_for_violations("very bad word", "g1", "u1", "m1", "c1")

        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].type, "timeout") # Should pick the second action
        self.assertEqual(actions[0].params["duration_seconds"], 300)

        self.mock_moderation_db.log_violation.assert_called_once()
        # Verify action_taken string in log
        log_args, _ = self.mock_moderation_db.log_violation.call_args
        self.assertEqual(log_args[7], "timeout ({'duration_seconds': 300, 'reason': 'escalated'})")
        self.assertEqual(log_args[9], "very bad word") # matched_content
        self.assertEqual(log_args[10], None) # duration_seconds in log_violation is for the log entry itself, not action param

    async def test_rule_disabled_in_detector(self):
        disabled_action = RuleAction(type="warning")
        disabled_rule_def = RuleDefinition(enabled=False, threshold=0.8, severity_score=5, actions=[disabled_action])

        mock_category = MagicMock(spec=RuleCategory)
        mock_category.rules = {"DisabledRule": disabled_rule_def}
        mock_category.name = "DisabledCat"
        self.mock_rule_engine.rule_categories = {"DisabledCat": mock_category}
        # get_rule would return this, but it's filtered out before content_analyzer.analyze_content is called

        # Content analyzer should not be called if all relevant rules are disabled
        actions = await self.detector.check_message_for_violations("any message", "g1", "u1", "m1", "c1")

        self.assertEqual(len(actions), 0)
        self.mock_content_analyzer.analyze_content.assert_not_called()
        self.mock_moderation_db.log_violation.assert_not_called()

if __name__ == '__main__':
    unittest.main()
