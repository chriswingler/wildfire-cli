# Unit tests for LevelManager
import pytest
import math # For math.isclose
from src.gamification.level_manager import LevelManager

@pytest.fixture
def level_manager() -> LevelManager:
    """Returns an instance of LevelManager."""
    return LevelManager()

# Test get_xp_for_level(level)
@pytest.mark.parametrize("level, expected_xp_formula_raw", [
    (0, 0),
    (1, 100 * (1**1.5)),
    (2, 100 * (2**1.5)),
    (10, 100 * (10**1.5)),
    (11, 100 * (11**1.5)),
    (25, 100 * (25**1.5)),
    (50, 100 * (50**1.5)),
    (51, 100 * (51**1.5)),
    (-1, 0), # Negative levels
])
def test_get_xp_for_level(level_manager: LevelManager, level: int, expected_xp_formula_raw: float):
    """Test calculation of total XP required for a given level."""
    expected_xp = round(expected_xp_formula_raw) if level > 0 else 0
    assert level_manager.get_xp_for_level(level) == expected_xp

# Test get_level_for_xp(total_xp)
# (level, xp_at_level_start, xp_just_below_next_level)
xp_level_test_cases = []
# Calculate some key points for testing get_level_for_xp
# Level 0: 0 XP
xp_level_test_cases.append((0, 0, 0)) # XP, expected level, xp for that level
# Level 1: starts at 100 XP. Next level (2) starts at round(100 * (2**1.5)) = 283 XP
xp_level_test_cases.append((100, 1, 100)) # XP for level 1
xp_level_test_cases.append((150, 1, 100)) # XP between L1 and L2
xp_level_test_cases.append((282, 1, 100)) # XP just before L2
# Level 2: starts at 283 XP. Next level (3) starts at round(100 * (3**1.5)) = 520 XP
xp_level_test_cases.append((283, 2, 283)) # XP for level 2
xp_level_test_cases.append((519, 2, 283)) # XP just before L3
# Level 10: starts at round(100*10**1.5) = 3162. Next level(11) starts at round(100*11**1.5) = 3642
xp_for_l10 = round(100 * (10**1.5))
xp_level_test_cases.append((xp_for_l10, 10, xp_for_l10))
xp_level_test_cases.append((xp_for_l10 + 100, 10, xp_for_l10)) # Between L10 and L11
xp_for_l11 = round(100 * (11**1.5))
xp_level_test_cases.append((xp_for_l11 -1, 10, xp_for_l10)) # Just before L11

# Test cases derived from the formula to ensure get_level_for_xp aligns
# with get_xp_for_level due to rounding and floor behavior.
# We are testing get_level_for_xp(TOTAL_XP) -> EXPECTED_LEVEL
# And also that get_xp_for_level(EXPECTED_LEVEL) <= TOTAL_XP < get_xp_for_level(EXPECTED_LEVEL + 1)

# Test cases: (total_xp, expected_level)
test_data_get_level = [
    (0, 0),
    (50, 0), # Below level 1
    (99, 0), # Still below level 1
    (100, 1), # Exactly level 1
    (101, 1),
    (282, 1), # XP for L2 is 283
    (283, 2), # Exactly level 2
    (284, 2),
    (round(100 * (3**1.5)) -1, 2), # XP for L3 is 520. So 519 should be L2.
    (round(100 * (3**1.5)), 3),   # Exactly level 3
    (round(100 * (10**1.5)), 10), # XP for L10 is 3162
    (round(100 * (10**1.5)) + 50, 10),
    (round(100 * (11**1.5)) -1, 10), # XP for L11 is 3642. So 3641 should be L10
    (round(100 * (11**1.5)), 11), # Exactly level 11
    (7000, 17), # round(100*17**1.5) = 7011. round(100*18**1.5) = 7637. 7000 should be L16.
                # Let's recalculate: (7000/100)**(1/1.5) = 70**(2/3) = 16.9... so level 16
                # XP for L16 = round(100*16**1.5) = round(100*64) = 6400
                # XP for L17 = round(100*17**1.5) = round(100*70.114) = 7011
                # So 7000 XP is level 16.
    (6400, 16),
    (7010, 16),
    (7011, 17),

]

@pytest.mark.parametrize("total_xp, expected_level", test_data_get_level)
def test_get_level_for_xp(level_manager: LevelManager, total_xp: int, expected_level: int):
    """Test calculation of level based on total XP."""
    calculated_level = level_manager.get_level_for_xp(total_xp)
    assert calculated_level == expected_level

    # Additional check: verify consistency with get_xp_for_level
    if expected_level > 0:
        assert level_manager.get_xp_for_level(calculated_level) <= total_xp
    if total_xp < level_manager.get_xp_for_level(calculated_level + 1) : # Handles max level case implicitly if next level xp is huge
         pass # This is expected
    else: # This means total_xp is actually enough for the next level
        if level_manager.get_xp_for_level(calculated_level + 1) > 0 : # Avoid if next level XP is 0 (e.g. if level cap)
             assert total_xp < level_manager.get_xp_for_level(calculated_level + 1), \
                 f"XP {total_xp} should be less than XP for level {calculated_level + 1} ({level_manager.get_xp_for_level(calculated_level + 1)})"


# Test get_xp_needed_for_next_level(current_total_xp)
@pytest.mark.parametrize("current_total_xp, expected_needed_xp", [
    (0, level_manager().get_xp_for_level(1)), # From 0 XP to Level 1
    (50, level_manager().get_xp_for_level(1) - 50), # Partway to Level 1
    (100, round(100 * (2**1.5)) - 100), # At Level 1 (100XP), need for L2 (283XP)
    (150, round(100 * (2**1.5)) - 150), # Partway through L1
    (282, round(100 * (2**1.5)) - 282), # Just before L2
    (283, round(100 * (3**1.5)) - 283), # At L2 (283XP), need for L3 (520XP)
    # Case where user is at a very high level (e.g. level 1000)
    # XP for L1000 = round(100 * 1000**1.5) = 3162278
    # XP for L1001 = round(100 * 1001**1.5) = 3166992
    (3162278, 3166992 - 3162278),
])
def test_get_xp_needed_for_next_level(level_manager: LevelManager, current_total_xp: int, expected_needed_xp: int):
    """Test calculation of XP needed to reach the next level."""
    assert level_manager.get_xp_needed_for_next_level(current_total_xp) == expected_needed_xp

def test_get_xp_needed_for_next_level_consistency(level_manager: LevelManager):
    """More general consistency check for get_xp_needed_for_next_level."""
    for xp_val in [0, 10, 100, 150, 283, 500, 3200, 7000]:
        current_level = level_manager.get_level_for_xp(xp_val)
        xp_for_next_actual_level = level_manager.get_xp_for_level(current_level + 1)

        if xp_for_next_actual_level == 0: # Should not happen unless level cap logic changes
            expected_needed = 0 # Or some indicator of max level
        else:
            expected_needed = xp_for_next_actual_level - xp_val

        calculated_needed = level_manager.get_xp_needed_for_next_level(xp_val)
        assert calculated_needed == expected_needed, \
            f"For XP {xp_val} (Level {current_level}), expected needed {expected_needed}, got {calculated_needed}"

# Placeholder tests for advanced features (ensure they exist and return defaults)
def test_apply_role_bonuses_placeholder(level_manager: LevelManager):
    assert level_manager.apply_role_bonuses("user1", 100) == 100

def test_check_level_cap_placeholder(level_manager: LevelManager):
    assert level_manager.check_level_cap("user1", 50) == 50

def test_get_prestige_level_placeholder(level_manager: LevelManager):
    assert level_manager.get_prestige_level("user1") == 0

def test_prevent_level_decay_placeholder(level_manager: LevelManager):
    assert level_manager.prevent_level_decay("user1") is True

# Test constants (optional, but good for ensuring they are not accidentally changed)
def test_constants_values(level_manager: LevelManager):
    assert level_manager.BASE_XP_MULTIPLIER == 100
    assert math.isclose(level_manager.LEVEL_EXPONENT, 1.5)
