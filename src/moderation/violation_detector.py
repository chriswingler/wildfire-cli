"""
Detects violations in messages based on rules and content analysis.

This module provides the `ViolationDetector` class, which orchestrates the
process of checking messages against defined moderation rules, analyzing
content, logging violations, and determining appropriate actions.
"""
import asyncio # Required for async def
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import logging

from src.moderation.rule_engine import RuleEngine, RuleDefinition, RuleAction
from src.moderation.content_analyzer import ContentAnalyzer, AnalysisResult
from src.database.moderation_db import ModerationDB

logger = logging.getLogger(__name__)

class ViolationDetector:
    """
    Orchestrates the detection of message content violations against moderation rules.
    It uses a RuleEngine to get rule definitions, a ContentAnalyzer to find violations,
    and a ModerationDB to log violations and manage user violation history.
    """
    def __init__(
        self,
        rule_engine: RuleEngine,
        content_analyzer: ContentAnalyzer,
        moderation_db: ModerationDB,
    ) -> None:
        """
        Initializes the ViolationDetector.

        Args:
            rule_engine: An instance of RuleEngine.
            content_analyzer: An instance of ContentAnalyzer.
            moderation_db: An instance of ModerationDB.
        """
        self.rule_engine = rule_engine
        self.content_analyzer = content_analyzer
        self.moderation_db = moderation_db

    async def check_message_for_violations( # pylint: disable=too-many-locals
        self,
        message_content: str,
        guild_id: str,
        user_id: str,
        message_id: str,
        channel_id: str,
    ) -> List[RuleAction]:
        """
        Asynchronously checks a message for violations against all enabled moderation rules.

        Args:
            message_content: The content of the message to check.
            guild_id: The ID of the guild where the message originated.
            user_id: The ID of the user who sent the message.
            message_id: The ID of the message.
            channel_id: The ID of the channel where the message was sent.

        Returns:
            A list of RuleAction objects representing the actions to be taken
            based on detected violations and user history.
        """
        all_actions_to_take: List[RuleAction] = []

        relevant_rules: List[Tuple[str, str, RuleDefinition]] = []
        try:
            for category_name, category in self.rule_engine.rule_categories.items():
                for rule_name, rule_def in category.rules.items():
                    if rule_def.enabled:
                        relevant_rules.append((category_name, rule_name, rule_def))
        except Exception as e:
            logger.error(f"Error compiling relevant rules: {e}")
            return [] # Cannot proceed if rule compilation fails

        if not relevant_rules:
            return []

        try:
            analysis_results: List[AnalysisResult] = await self.content_analyzer.analyze_content(
                message_content=message_content,
                guild_id=guild_id,
                user_id=user_id,
                relevant_rules=relevant_rules,
            )
        except Exception as e:
            logger.error(f"Error during content analysis for message {message_id}: {e}")
            return [] # Cannot proceed if analysis fails

        for result in analysis_results:
            action_to_log_str = "unknown"
            determined_action_obj: Optional[RuleAction] = None

            try:
                violated_rule_definition = self.rule_engine.get_rule(
                    result.violated_rule_category, result.violated_rule_name
                )

                if violated_rule_definition and violated_rule_definition.actions:
                    user_status = await self.moderation_db.get_user_violation_status(guild_id=guild_id, user_id=user_id)
                    current_warning_level = 0
                    if user_status and user_status.get('warning_level') is not None:
                        current_warning_level = user_status['warning_level']

                    # Simple escalation: if warning level > 1 and multiple actions exist, take the second. Otherwise, first.
                    if current_warning_level > 1 and len(violated_rule_definition.actions) > 1:
                        determined_action_obj = violated_rule_definition.actions[1]
                    elif violated_rule_definition.actions: # Ensure there's at least one action
                        determined_action_obj = violated_rule_definition.actions[0]

                    if determined_action_obj:
                        all_actions_to_take.append(determined_action_obj)
                        action_to_log_str = determined_action_obj.type
                        if determined_action_obj.params:
                            action_to_log_str += f" ({determined_action_obj.params})"

                        # Conceptual comment: Appeal System Trigger
                        # if determined_action_obj.type == "ban":
                        #     logger.info(f"Ban action triggered for user {user_id}. Logging for potential appeal.")
                        #     # call_appeal_system_hook(user_id, guild_id, result, determined_action_obj)

                # Log the violation
                await self.moderation_db.log_violation(
                    guild_id=guild_id,
                    user_id=user_id,
                    message_id=message_id,
                    channel_id=channel_id,
                    violation_type=result.violated_rule_category,
                    rule_name=result.violated_rule_name,
                    severity=result.severity,
                    action_taken=action_to_log_str,
                    matched_content=result.matched_content,
                    # violation_timestamp is handled by ModerationDB if not passed
                )

                # Update user's violation summary
                await self.moderation_db.update_user_violation_summary(
                    guild_id=guild_id,
                    user_id=user_id,
                    severity_increment=result.severity,
                    violation_timestamp=datetime.now() # Timestamp of this specific violation event
                )

            except Exception as e:
                logger.error(f"Error processing violation result for rule '{result.violated_rule_name}' on message {message_id}: {e}")
                # Continue to process other results if one fails

        return all_actions_to_take
