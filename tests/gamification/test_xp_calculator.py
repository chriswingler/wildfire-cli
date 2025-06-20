# Unit tests for XPCalculator
import pytest
from src.gamification.xp_calculator import XPCalculator

@pytest.fixture
def xp_calculator() -> XPCalculator:
    """Returns an instance of XPCalculator."""
    return XPCalculator()

def test_calculate_xp_base(xp_calculator: XPCalculator):
    """Test base XP for a simple message."""
    assert xp_calculator.calculate_xp("Hello") == XPCalculator.BASE_MESSAGE_XP

def test_calculate_xp_spam(xp_calculator: XPCalculator):
    """Test XP for a message flagged as spam."""
    assert xp_calculator.calculate_xp("This is spam", is_spam=True) == XPCalculator.SPAM_LOW_QUALITY_XP

def test_calculate_xp_helpful_answer(xp_calculator: XPCalculator):
    """Test XP for a helpful answer."""
    expected_xp = XPCalculator.BASE_MESSAGE_XP + XPCalculator.HELPFUL_ANSWER_XP
    assert xp_calculator.calculate_xp("This is helpful", is_helpful_answer=True) == expected_xp

def test_calculate_xp_problem_solution(xp_calculator: XPCalculator):
    """Test XP for a problem solution."""
    expected_xp = XPCalculator.BASE_MESSAGE_XP + XPCalculator.PROBLEM_SOLUTION_XP
    assert xp_calculator.calculate_xp("Here is the solution", is_problem_solution=True) == expected_xp

def test_calculate_xp_quality_discussion(xp_calculator: XPCalculator):
    """Test XP for a quality discussion contribution."""
    expected_xp = XPCalculator.BASE_MESSAGE_XP + XPCalculator.QUALITY_DISCUSSION_XP
    assert xp_calculator.calculate_xp("Good point", is_quality_discussion=True) == expected_xp

def test_calculate_xp_creative_content(xp_calculator: XPCalculator):
    """Test XP for creative content."""
    expected_xp = XPCalculator.BASE_MESSAGE_XP + XPCalculator.CREATIVE_CONTENT_XP
    assert xp_calculator.calculate_xp("My new art", is_creative_content=True) == expected_xp

def test_calculate_xp_community_assistance(xp_calculator: XPCalculator):
    """Test XP for community assistance."""
    expected_xp = XPCalculator.BASE_MESSAGE_XP + XPCalculator.COMMUNITY_ASSISTANCE_XP
    assert xp_calculator.calculate_xp("Let me help you", is_community_assistance=True) == expected_xp

def test_calculate_xp_multiple_flags(xp_calculator: XPCalculator):
    """Test XP calculation with multiple positive flags."""
    expected_xp = (
        XPCalculator.BASE_MESSAGE_XP +
        XPCalculator.HELPFUL_ANSWER_XP +
        XPCalculator.QUALITY_DISCUSSION_XP +
        XPCalculator.CREATIVE_CONTENT_XP
    )
    assert xp_calculator.calculate_xp(
        "A helpful, quality, creative post",
        is_helpful_answer=True,
        is_quality_discussion=True,
        is_creative_content=True
    ) == expected_xp

def test_calculate_xp_spam_overrides_positive(xp_calculator: XPCalculator):
    """Test that spam flag overrides positive contributions."""
    assert xp_calculator.calculate_xp(
        "Helpful spam? No.",
        is_helpful_answer=True,
        is_quality_discussion=True,
        is_spam=True
    ) == XPCalculator.SPAM_LOW_QUALITY_XP

# Tests for apply_diminishing_returns
def test_apply_diminishing_returns_no_effect(xp_calculator: XPCalculator):
    """Test diminishing returns when message count is not a multiple of 10."""
    user_id = "user1"
    initial_xp = 10
    message_count = 5
    assert xp_calculator.apply_diminishing_returns(user_id, initial_xp, message_count) == initial_xp

def test_apply_diminishing_returns_effect_on_10th_message(xp_calculator: XPCalculator):
    """Test diminishing returns on the 10th message."""
    user_id = "user2"
    initial_xp = 10
    message_count = 10
    assert xp_calculator.apply_diminishing_returns(user_id, initial_xp, message_count) == initial_xp // 2

def test_apply_diminishing_returns_effect_on_20th_message(xp_calculator: XPCalculator):
    """Test diminishing returns on the 20th message."""
    user_id = "user3"
    initial_xp = 20
    message_count = 20
    assert xp_calculator.apply_diminishing_returns(user_id, initial_xp, message_count) == initial_xp // 2

def test_apply_diminishing_returns_zero_initial_xp(xp_calculator: XPCalculator):
    """Test diminishing returns with zero initial XP."""
    user_id = "user4"
    initial_xp = 0
    message_count = 10
    assert xp_calculator.apply_diminishing_returns(user_id, initial_xp, message_count) == 0

def test_apply_diminishing_returns_odd_initial_xp(xp_calculator: XPCalculator):
    """Test diminishing returns with odd initial XP, expecting floor division."""
    user_id = "user5"
    initial_xp = 5
    message_count = 10
    assert xp_calculator.apply_diminishing_returns(user_id, initial_xp, message_count) == 2 # 5 // 2 = 2

# Tests for assess_contribution_value (placeholder)
def test_assess_contribution_value_structure(xp_calculator: XPCalculator):
    """Test the structure and types of the dictionary returned by assess_contribution_value."""
    result = xp_calculator.assess_contribution_value("Test message")
    assert isinstance(result, dict)

    expected_keys = [
        'is_helpful_answer', 'is_problem_solution', 'is_quality_discussion',
        'is_creative_content', 'is_community_assistance', 'is_spam'
    ]
    for key in expected_keys:
        assert key in result
        assert isinstance(result[key], bool)

def test_assess_contribution_value_not_used_in_calc_xp(xp_calculator: XPCalculator):
    """
    This test is more conceptual: it verifies that the current calculate_xp
    doesn't actually use the output of assess_contribution_value, as per current design.
    The flags are passed directly to calculate_xp.
    """
    # assess_contribution_value might return all False by default or randomly.
    # calculate_xp relies on its direct boolean arguments.
    # If assess_contribution_value were to influence calculate_xp internally,
    # this test's assumptions would need to change.
    base_xp_only = xp_calculator.calculate_xp("test")
    assert base_xp_only == XPCalculator.BASE_MESSAGE_XP

    xp_with_flag = xp_calculator.calculate_xp("test helpful", is_helpful_answer=True)
    assert xp_with_flag == XPCalculator.BASE_MESSAGE_XP + XPCalculator.HELPFUL_ANSWER_XP
    # This doesn't directly test assess_contribution_value, but confirms calculate_xp's behavior.
    # A true test of their interaction would require assess_contribution_value to be called
    # *by* calculate_xp, which is not the current design.
    # The current design is:
    # 1. Call ContributionAnalyzer.analyze_contribution (external to XPCalculator)
    # 2. Pass results of ^ to XPCalculator.calculate_xp
    # XPCalculator.assess_contribution_value is a standalone placeholder within XPCalculator,
    # perhaps for a different workflow or future internal LLM call.
    # For now, we just test its output structure.
    pass
