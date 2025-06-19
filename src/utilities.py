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

    def __init__(self):
        """Initialize cooldown tracking dictionaries."""
        self.user_cooldowns = {}
        self.channel_cooldowns = {}
        self.reaction_cooldowns = {}

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