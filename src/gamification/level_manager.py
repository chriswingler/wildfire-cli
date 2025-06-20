"""
This module defines the LevelManager class for managing user levels based on XP.
"""

import math

class LevelManager:
    """
    Manages user level progression based on accumulated XP.
    Uses an exponential formula for XP requirements per level.
    """

    BASE_XP_MULTIPLIER = 100
    LEVEL_EXPONENT = 1.5

    def __init__(self):
        """
        Initializes the LevelManager.
        """
        pass

    def get_xp_for_level(self, level: int) -> int:
        """
        Calculates the total XP required to reach a specific level.

        Args:
            level: The target level.

        Returns:
            The total XP required for that level. Returns 0 for levels below 1.
        """
        if level < 1:
            return 0
        # Formula: total_xp_for_level(level) = round(BASE_XP_MULTIPLIER * (level ** LEVEL_EXPONENT))
        return round(self.BASE_XP_MULTIPLIER * (level ** self.LEVEL_EXPONENT))

    def get_level_for_xp(self, total_xp: int) -> int:
        """
        Calculates a user's level based on their total accumulated XP.

        Args:
            total_xp: The total accumulated XP of the user.

        Returns:
            The user's current level. Level 0 if XP is less than XP for level 1.
        """
        if total_xp < self.get_xp_for_level(1): # XP for level 1 is the minimum threshold
            return 0

        # Estimate level using the inverse of the XP formula
        # level = (xp / multiplier) ^ (1 / exponent)
        # Add a small epsilon to handle potential floating point inaccuracies before floor,
        # though direct calculation and adjustment is often more robust.
        if self.BASE_XP_MULTIPLIER == 0: # Avoid division by zero
            return 1 # Or some other appropriate handling

        # Initial guess using the formula's inverse
        # Must handle total_xp = 0 if get_xp_for_level(1) is also 0 (e.g. if base_xp_multiplier is 0)
        try:
            # Ensure the argument to power is not negative if total_xp is low and exponent is fractional
            ratio = total_xp / self.BASE_XP_MULTIPLIER
            if ratio < 0: ratio = 0 # Should not happen with positive XP
            estimated_level = math.floor(ratio ** (1 / self.LEVEL_EXPONENT))
        except ValueError: # pragma: no cover (should be caught by ratio < 0)
            estimated_level = 1

        if estimated_level < 1: # Should at least be level 1 if past the initial check
            estimated_level = 1

        # Adjust the estimated level due to rounding in get_xp_for_level
        # Loop a few times to find the correct level. Usually, it will be found in 1-2 iterations.
        # Max iterations safeguard against unexpected edge cases with floating point math.
        for _ in range(5): # Iterate a few times to find the correct level band
            xp_at_estimated_level = self.get_xp_for_level(estimated_level)
            xp_at_next_estimated_level = self.get_xp_for_level(estimated_level + 1)

            if xp_at_estimated_level <= total_xp < xp_at_next_estimated_level:
                return estimated_level
            elif total_xp < xp_at_estimated_level:
                # total_xp is less than what's needed for estimated_level, so level must be lower
                estimated_level -= 1
                if estimated_level < 1: return 1 # Should not go below 1 if initial check passed
            else: # total_xp >= xp_at_next_estimated_level
                # total_xp is enough for the next level, so current estimate is too low
                estimated_level += 1

        # Fallback or error if level not found after adjustments - this indicates a potential issue
        # For safety, return the last valid estimate that's likely close.
        # Or, revert to a known safe calculation if this path is reached.
        # Given the check `total_xp < self.get_xp_for_level(1)` returns 0,
        # and `estimated_level` starts >=1, this path should ideally not be hit frequently.
        # If it is, the formula or adjustment logic might need review for extreme values.
        # Let's ensure the final returned level's XP is not greater than total_xp.
        while self.get_xp_for_level(estimated_level) > total_xp and estimated_level > 0:
            estimated_level -=1
        if estimated_level == 0 and total_xp >= self.get_xp_for_level(1): # If it became 0 but shouldn't
            return 1 # pragma: no cover
        return estimated_level # pragma: no cover

    def get_xp_needed_for_next_level(self, current_total_xp: int) -> int:
        """
        Calculates how much more XP a user needs to reach the next level.

        Args:
            current_total_xp: The user's current total accumulated XP.

        Returns:
            The amount of XP needed to reach the next level.
            Returns 0 if the user is at a theoretical max level or in an error state.
        """
        current_level = self.get_level_for_xp(current_total_xp)
        xp_for_next_level = self.get_xp_for_level(current_level + 1)

        if xp_for_next_level <= current_total_xp : # Should not happen with correct get_level_for_xp
             return 0 # Already at or past next level's requirement (e.g. max level reached)

        needed_xp = xp_for_next_level - current_total_xp
        return needed_xp

    # --- Placeholders for Advanced Features ---

    def apply_role_bonuses(self, user_id: str, current_xp: int) -> int:
        """
        Applies role-based XP bonuses (placeholder).

        Args:
            user_id: The ID of the user.
            current_xp: The current XP amount before bonuses.

        Returns:
            The XP amount after applying role bonuses.
        """
        print(f"Applying role bonuses for user {user_id} to XP {current_xp}...") # Log
        return current_xp

    def check_level_cap(self, user_id: str, current_level: int) -> int:
        """
        Checks and applies any level caps for the user (placeholder).

        Args:
            user_id: The ID of the user.
            current_level: The user's current calculated level.

        Returns:
            The user's level after considering any caps.
        """
        print(f"Checking level cap for user {user_id} at level {current_level}...") # Log
        # Example cap:
        # MAX_LEVEL_CAP = 100
        # if current_level > MAX_LEVEL_CAP:
        # return MAX_LEVEL_CAP
        return current_level

    def get_prestige_level(self, user_id: str) -> int:
        """
        Gets the user's prestige level (placeholder).
        Prestige levels could be achieved after hitting a max level and resetting.

        Args:
            user_id: The ID of the user.

        Returns:
            The user's prestige level (default 0).
        """
        print(f"Getting prestige level for user {user_id}...") # Log
        return 0

    def prevent_level_decay(self, user_id: str) -> bool:
        """
        Checks if level decay should be prevented for the user (placeholder).
        This might be based on subscription status, recent activity, etc.

        Args:
            user_id: The ID of the user.

        Returns:
            True if level decay is prevented, False otherwise.
        """
        print(f"Checking level decay prevention for user {user_id}...") # Log
        return True
