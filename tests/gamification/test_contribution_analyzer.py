# Unit tests for ContributionAnalyzer
import pytest
import pytest_asyncio # For async fixtures
from unittest.mock import AsyncMock # For mocking async methods
from src.gamification.contribution_analyzer import ContributionAnalyzer
# LLMService is now a dependency, but we'll mock its methods,
# so direct import of LLMService itself isn't strictly needed for mocking.

@pytest_asyncio.fixture # Async fixture
async def analyzer(mocker) -> ContributionAnalyzer: # Add mocker fixture
    """
    Returns an instance of ContributionAnalyzer with a mocked LLMService.
    The llm_service.analyze_message_content method will be an AsyncMock.
    """
    # Mock the LLMService instance within ContributionAnalyzer
    # This approach avoids needing to import LLMService here directly if it's complex
    # or if we only want to control its interaction with ContributionAnalyzer.
    mocked_llm_service_instance = AsyncMock()

    # Patch the LLMService class where it's imported by contribution_analyzer.py
    # Assuming 'src.gamification.contribution_analyzer.LLMService' is the correct path
    mocker.patch('src.gamification.contribution_analyzer.LLMService', return_value=mocked_llm_service_instance)

    # Now, when ContributionAnalyzer is instantiated, it will use the mocked LLMService
    ca = ContributionAnalyzer(llm_api_key="test_key_for_analyzer_fixture")
    ca.llm_service = mocked_llm_service_instance # Ensure the instance uses our specific mock
    return ca


@pytest.mark.asyncio
async def test_analyze_contribution_maps_llm_results_correctly(analyzer: ContributionAnalyzer):
    """
    Test that analyze_contribution correctly maps results from a mocked LLMService.
    """
    message_content = "This is a helpful message about solving a problem with python."
    user_id = "user_test"
    channel_id = "channel_test"

    # Define the expected raw output from the (mocked) LLMService
    mock_llm_output = {
        'helpfulness_score': 0.8,       # Should map to is_helpful_answer = True
        'is_problem_solution': True,    # Should map directly
        'quality_score': 0.7,           # Should map to is_quality_discussion = True
        'sentiment_score': 0.5,
        'is_spam': False,
        'identified_keywords': ['python', 'problem', 'helpful'],
        'primary_topic': 'technical question'
    }
    analyzer.llm_service.analyze_message_content = AsyncMock(return_value=mock_llm_output)

    result = await analyzer.analyze_contribution(message_content, user_id, channel_id)

    # Assert that analyze_message_content was called correctly
    analyzer.llm_service.analyze_message_content.assert_called_once_with(
        message_content,
        ["helpfulness", "problem_solving", "quality", "sentiment", "spam", "keywords", "topic"]
    )

    # Assertions based on the mapping logic in ContributionAnalyzer
    assert result['is_helpful_answer'] is True
    assert result['is_problem_solution'] is True
    assert result['is_quality_discussion'] is True # 0.7 > 0.6
    assert result['is_creative_content'] is False # Default placeholder
    # Community assistance: helpfulness_score > 0.5 AND quality_score > 0.5
    assert result['is_community_assistance'] is True # 0.8 > 0.5 and 0.7 > 0.5
    # Spam: llm_raw_results.get('is_spam', False) or quality_score < 0.2
    assert result['is_spam_or_low_quality'] is False # False or (0.7 < 0.2 is False)

    assert result['detected_keywords'] == ['python', 'problem', 'helpful']
    assert result['sentiment_score'] == 0.5
    assert result['raw_helpfulness_score'] == 0.8
    assert result['raw_quality_score'] == 0.7
    assert result['primary_topic'] == 'technical question'
    assert result['raw_llm_data'] == mock_llm_output


@pytest.mark.asyncio
async def test_analyze_contribution_low_quality_thresholds(analyzer: ContributionAnalyzer):
    """Test how low quality scores from LLM affect flags."""
    message_content = "short bad msg"
    user_id = "uq_low"
    channel_id = "cq_low"

    mock_llm_output = {
        'helpfulness_score': 0.1,       # is_helpful_answer = False (0.1 <= 0.65)
        'is_problem_solution': False,
        'quality_score': 0.15,          # is_quality_discussion = False (0.15 <= 0.6)
                                        # is_spam_or_low_quality = True (0.15 < 0.2)
        'sentiment_score': -0.8,
        'is_spam': False,               # Spam is False from LLM direct
        'identified_keywords': ['short', 'bad'],
        'primary_topic': 'complaint'
    }
    analyzer.llm_service.analyze_message_content = AsyncMock(return_value=mock_llm_output)

    result = await analyzer.analyze_contribution(message_content, user_id, channel_id)

    assert result['is_helpful_answer'] is False
    assert result['is_problem_solution'] is False
    assert result['is_quality_discussion'] is False
    assert result['is_community_assistance'] is False # 0.1 not > 0.5
    assert result['is_spam_or_low_quality'] is True # quality_score 0.15 < 0.2
    assert result['sentiment_score'] == -0.8

@pytest.mark.asyncio
async def test_analyze_contribution_llm_detects_spam(analyzer: ContributionAnalyzer):
    """Test when LLM directly flags content as spam."""
    message_content = "BUY MY STUFF NOW CHEAP!!!"
    user_id = "uq_spam"
    channel_id = "cq_spam"

    mock_llm_output = {
        'helpfulness_score': 0.0,
        'is_problem_solution': False,
        'quality_score': 0.05,          # Very low quality
        'sentiment_score': 0.1,
        'is_spam': True,                # LLM says it's spam
        'identified_keywords': ['buy', 'cheap'],
        'primary_topic': 'advertisement'
    }
    analyzer.llm_service.analyze_message_content = AsyncMock(return_value=mock_llm_output)

    result = await analyzer.analyze_contribution(message_content, user_id, channel_id)

    assert result['is_spam_or_low_quality'] is True # Directly from llm_raw_results.get('is_spam', False)

@pytest.mark.asyncio
async def test_analyze_contribution_missing_keys_from_llm(analyzer: ContributionAnalyzer):
    """Test robustness if LLM response is missing some expected keys."""
    message_content = "A message."
    user_id = "uq_missing"
    channel_id = "cq_missing"

    mock_llm_output = { # Intentionally missing some keys
        'helpfulness_score': 0.7,
        # 'is_problem_solution': missing
        'quality_score': 0.75,
        # 'sentiment_score': missing
        'is_spam': False,
        # 'identified_keywords': missing
        # 'primary_topic': missing
    }
    analyzer.llm_service.analyze_message_content = AsyncMock(return_value=mock_llm_output)

    result = await analyzer.analyze_contribution(message_content, user_id, channel_id)

    assert result['is_helpful_answer'] is True # 0.7 > 0.65
    assert result['is_problem_solution'] is False # Default from .get(, False)
    assert result['is_quality_discussion'] is True # 0.75 > 0.6
    assert result['is_community_assistance'] is True # 0.7 > 0.5 and 0.75 > 0.5
    assert result['is_spam_or_low_quality'] is False # is_spam is False, quality 0.75 not < 0.2
    assert result['detected_keywords'] == [] # Default from .get(, [])
    assert result['sentiment_score'] == 0.0 # Default from .get(, 0.0)
    assert result['primary_topic'] == 'unknown' # Default from .get(..., 'unknown')
    assert result['raw_llm_data'] == mock_llm_output


def test_contribution_analyzer_init_default_key():
    """Test that ContributionAnalyzer initializes LLMService with the default dummy key."""
    # This test relies on the structure and not mocking LLMService itself at class level.
    # It effectively tests that `LLMService()` is called within `ContributionAnalyzer.__init__`.
    # To do this without mocker, we'd need to inspect the created LLMService instance.
    # Or, if LLMService prints on init, we could capture stdout.
    # Given current setup, this test is more about conceptual flow.
    # A more direct test would be:
    # analyzer = ContributionAnalyzer()
    # assert isinstance(analyzer.llm_service, LLMService)
    # assert analyzer.llm_service.api_key == "DUMMY_API_KEY_FOR_NOW"
    # However, the fixture already patches LLMService, so this standalone test needs care.

    # For this test, let's instantiate analyzer without the fixture's global patch
    # by temporarily disabling it IF that's how the fixture works, or by directly
    # importing LLMService and checking.

    # Simplest way assuming LLMService is importable for test context:
    from src.gamification.llm_service import LLMService as RealLLMService
    temp_analyzer = ContributionAnalyzer()
    assert isinstance(temp_analyzer.llm_service, RealLLMService)
    assert temp_analyzer.llm_service.api_key == "DUMMY_API_KEY_FOR_NOW"

def test_contribution_analyzer_init_custom_key():
    from src.gamification.llm_service import LLMService as RealLLMService
    custom_key = "MY_REAL_API_KEY"
    temp_analyzer = ContributionAnalyzer(llm_api_key=custom_key)
    assert isinstance(temp_analyzer.llm_service, RealLLMService)
    assert temp_analyzer.llm_service.api_key == custom_key

# Removed old tests for:
# - test_detect_helpful_answer
# - test_detect_problem_solution
# - test_score_knowledge_sharing
# - test_recognize_community_leadership
# - test_track_creative_content
# - test_analyze_contribution_structure_and_types (replaced by more specific mapping tests)
# - test_analyze_contribution_spam_detection (logic now inside LLMService or mapping)
# - test_analyze_contribution_keyword_detection (logic now inside LLMService)
# - test_analyze_contribution_quality_discussion_logic (logic now inside LLMService)
# - test_init_with_llm_config (replaced by more direct __init__ tests)
