"""
@file utilities.py
@brief Core support components for wildfire Discord bot
@details Simplified from BlazeBot - only essential utilities following YAGNI principle
"""

from datetime import datetime, timedelta


class CooldownManager:
    """
    @brief Rate limiting system for bot interactions
    @details Manages cooldowns for:
    - User commands
    - Channel interactions  
    - Message reactions
    """

from typing import Optional # Added for new methods

class CooldownManager:
    """
    @brief Rate limiting system for bot interactions
    @details Manages cooldowns for:
    - User commands
    - Channel interactions
    - Message reactions
    - Moderation actions (e.g., mutes, send message bans)
    """

    def __init__(self):
        """Initialize cooldown tracking dictionaries."""
        self.user_cooldowns = {}
        self.channel_cooldowns = {}
        self.reaction_cooldowns = {}
        self.moderation_action_cooldowns = {} # For specific moderation actions

    # Conceptual comment:
    # A list of moderator role IDs or user IDs could be stored here or passed
    # to check_moderation_cooldown to allow moderators to bypass cooldowns.
    # self.moderator_ids = [123456789012345678, ...]

    def check(self, message):
        """
        @brief Check if user/channel is off cooldown
        @param message discord.Message object to check
        @return True if allowed to respond, False if in cooldown
        @details Checks:
        - 3-minute user cooldown
        - 30-second channel cooldown
        """
        user_ok = message.author.id not in self.user_cooldowns or \
            (datetime.now() -
             self.user_cooldowns[message.author.id]) > timedelta(seconds=180)
        channel_ok = message.channel.id not in self.channel_cooldowns or \
            (datetime.now() -
             self.channel_cooldowns[message.channel.id]) > timedelta(seconds=30)
        return user_ok and channel_ok

    def update(self, message):
        """
        @brief Update cooldown timers after response
        @param message discord.Message that triggered cooldown
        """
        self.user_cooldowns[message.author.id] = datetime.now()
        self.channel_cooldowns[message.channel.id] = datetime.now()

    def check_reaction(self, message):
        """
        @brief Check if reactions are allowed on message
        @param message discord.Message to check
        @return True if allowed to react, False if in cooldown
        @details Enforces 1-second reaction cooldown per message
        """
        key = f"{message.channel.id}-{message.id}"
        last_react = self.reaction_cooldowns.get(key, datetime.min)
        return (datetime.now() - last_react) > timedelta(seconds=1)

    def update_reaction(self, message):
        """
        @brief Update reaction cooldown tracker
        @param message discord.Message that received reaction
        """
        key = f"{message.channel.id}-{message.id}"
        self.reaction_cooldowns[key] = datetime.now()

    def check_moderation_cooldown(self, user_id: str, action_type: str) -> bool:
        """
        @brief Checks if a user is currently under a moderation cooldown for a specific action_type.
        @param user_id The ID of the user.
        @param action_type The type of moderation action (e.g., "send_message_ban").
        @return True if the user is *not* on cooldown (action allowed), False otherwise.
        """
        # Conceptual comment: Moderator Bypass
        # if user_id in self.moderator_ids:
        #     return True # Moderators always bypass

        cooldown_key = f"{user_id}_{action_type}"
        if cooldown_key in self.moderation_action_cooldowns:
            if datetime.now() < self.moderation_action_cooldowns[cooldown_key]:
                return False  # User is on cooldown
            else:
                # Cooldown has expired, remove it
                del self.moderation_action_cooldowns[cooldown_key]
                return True # Cooldown expired
        return True # Not on cooldown

    def apply_moderation_cooldown(self, user_id: str, action_type: str, duration_seconds: int):
        """
        @brief Applies a cooldown for action_type to the user_id for duration_seconds.
        @param user_id The ID of the user.
        @param action_type The type of moderation action.
        @param duration_seconds The duration of the cooldown in seconds.
        """
        cooldown_key = f"{user_id}_{action_type}"
        cooldown_end_time = datetime.now() + timedelta(seconds=duration_seconds)
        self.moderation_action_cooldowns[cooldown_key] = cooldown_end_time
        # Conceptual comment: Appeal System Trigger
        # if action_type == "ban" or duration_seconds > 3600: # e.g., for long timeouts or bans
        #     print(f"User {user_id} received action {action_type} for {duration_seconds}s. Consider logging for appeal.")
        #     # trigger_appeal_process(user_id, action_type, duration_seconds)

    def get_active_moderation_cooldown_duration(self, user_id: str, action_type: str) -> Optional[int]:
        """
        @brief If a user has an active cooldown for action_type, returns the remaining duration in seconds.
        @param user_id The ID of the user.
        @param action_type The type of moderation action.
        @return Remaining duration in seconds if active cooldown, else None.
        """
        cooldown_key = f"{user_id}_{action_type}"
        if cooldown_key in self.moderation_action_cooldowns:
            remaining_time = self.moderation_action_cooldowns[cooldown_key] - datetime.now()
            if remaining_time.total_seconds() > 0:
                return int(remaining_time.total_seconds())
            else:
                # Cooldown has expired, remove it and return None
                del self.moderation_action_cooldowns[cooldown_key]
                return None
        return None