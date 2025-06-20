import unittest
from unittest.mock import patch, AsyncMock
from src.analytics.trend_analyzer import (
    get_sentiment_trend,
    get_topic_trends,
    get_community_growth_patterns,
    calculate_engagement_quality_score,
    calculate_community_health_score,
)
from datetime import date, timedelta

class TestTrendAnalyzer(unittest.IsolatedAsyncioTestCase):

    @patch('src.analytics.trend_analyzer._execute_query')
    async def test_get_sentiment_trend_placeholder(self, mock_execute_query):
        """Test placeholder get_sentiment_trend returns mock data."""
        # This function is a placeholder, so we test its mock output.
        # If it were to query, the mock setup would be like:
        # mock_execute_query.return_value = [("2023-01-01", 0.6), ("2023-01-02", 0.7)]

        start_date = "2023-01-01"
        end_date = "2023-01-02" # Short period for mock

        # The actual placeholder returns a generated list based on dates
        # not from _execute_query directly.
        # So we don't need to mock _execute_query for the current placeholder logic
        # unless it was changed to actually call it.
        # The current placeholder directly constructs and returns data.

        # Re-patching if the placeholder was changed to call _execute_query:
        # with patch('src.analytics.trend_analyzer._execute_query', new_callable=AsyncMock) as actual_mock_eq:
        # actual_mock_eq.return_value = [("2023-01-01", 0.6), ("2023-01-02", 0.7)]

        trend = await get_sentiment_trend("dummy_db_path", start_date, end_date)

        self.assertTrue(isinstance(trend, list))
        if trend: # If placeholder returns data
            self.assertTrue(isinstance(trend[0], tuple))
            self.assertEqual(len(trend[0]), 2) # Date, score
            self.assertEqual(trend[0][0], "2023-01-01")

    @patch('src.analytics.trend_analyzer._execute_query')
    async def test_get_topic_trends_placeholder(self, mock_execute_query):
        """Test placeholder get_topic_trends returns mock data."""
        # Similar to sentiment, this is a placeholder.
        start_date = "2023-01-01"
        end_date = "2023-01-02"
        topics = await get_topic_trends("dummy_db_path", start_date, end_date)

        self.assertTrue(isinstance(topics, list))
        if topics: # If placeholder returns data
            self.assertTrue(isinstance(topics[0], dict))
            self.assertIn("topic", topics[0])

    @patch('src.analytics.trend_analyzer._execute_query')
    async def test_get_community_growth_patterns(self, mock_execute_query):
        """Test get_community_growth_patterns with mock data."""
        mock_execute_query.return_value = [
            ("2023-01-01", 100, 5, 1), # date, total_members, new_members, left_members
            ("2023-01-02", 104, 2, 0),
        ]

        start_date = "2023-01-01"
        end_date = "2023-01-02"
        patterns = await get_community_growth_patterns("dummy_db_path", start_date, end_date)

        expected_patterns = [
            ("2023-01-01", 100, 5, 1),
            ("2023-01-02", 104, 2, 0),
        ]
        self.assertEqual(patterns, expected_patterns)
        mock_execute_query.assert_called_once_with(
            "dummy_db_path",
            unittest.mock.ANY, # SQL query
            (start_date, end_date)
        )

    @patch('src.analytics.trend_analyzer._execute_query')
    async def test_calculate_engagement_quality_score(self, mock_execute_query):
        """Test calculate_engagement_quality_score with specific user data."""
        # Mock return for: SUM(message_count), SUM(reaction_count), SUM(voice_minutes)
        mock_execute_query.return_value = [(10, 20, 30.0)] # msg, react, voice

        user_id = "user123"
        end_date_str = "2023-01-30"
        lookback_days = 30

        score = await calculate_engagement_quality_score("dummy_db_path", user_id, end_date_str, lookback_days)

        # Expected score: (10 * 0.5) + (20 * 0.3) + (30.0 * 0.2)
        # = 5 + 6 + 6 = 17.0
        expected_score = 17.0
        self.assertAlmostEqual(score, expected_score, places=2)

        start_dt = date.fromisoformat(end_date_str) - timedelta(days=lookback_days - 1)
        start_date_str_calc = start_dt.isoformat()

        mock_execute_query.assert_called_once_with(
            "dummy_db_path",
            unittest.mock.ANY, # SQL query
            (user_id, start_date_str_calc, end_date_str)
        )

    @patch('src.analytics.trend_analyzer._execute_query')
    async def test_calculate_engagement_quality_score_no_activity(self, mock_execute_query):
        """Test engagement score when user has no activity."""
        mock_execute_query.return_value = [(None, None, None)]
        score = await calculate_engagement_quality_score("dummy_db_path", "user123", "2023-01-30", 30)
        self.assertEqual(score, 0.0)

    @patch('src.analytics.trend_analyzer._execute_query')
    async def test_calculate_community_health_score(self, mock_execute_query):
        """Test calculate_community_health_score with various mocked metrics."""
        # This is more complex due to multiple queries or one complex query.
        # Current implementation uses two queries.
        # Query 1: SUM(message_count), SUM(reaction_count), COUNT(DISTINCT user_id)
        # Query 2: SUM(new_members), SUM(left_members)

        mock_execute_query.side_effect = [
            [(1000, 500, 50)],  # user_activity_res: total_messages, total_reactions, distinct_users
            [(20, 5)],          # growth_res: new_members, left_members
        ]

        guild_id = "guild123"
        end_date_str = "2023-01-30"
        lookback_days = 30

        score = await calculate_community_health_score("dummy_db_path", guild_id, end_date_str, lookback_days)

        # Expected calculation based on mock data and formula in calculate_community_health_score:
        # total_messages = 1000, total_reactions = 500, distinct_users = 50
        # new_members = 20, left_members = 5, net_growth = 15
        # messages_score = min(1000 * 0.02, 40) = min(20, 40) = 20
        # reactions_score = min(500 * 0.03, 30) = min(15, 30) = 15
        # active_users_score = min(50 * 0.5, 20) = min(25, 20) = 20
        # net_growth_score = max(min(15 * 1, 10), -10) = max(min(15,10), -10) = max(10, -10) = 10
        # community_health = 20 + 15 + 20 + 10 = 65
        expected_score = 65.0
        self.assertAlmostEqual(score, expected_score, places=2)

        start_dt = date.fromisoformat(end_date_str) - timedelta(days=lookback_days-1)
        start_date_str_calc = start_dt.isoformat()

        self.assertEqual(mock_execute_query.call_count, 2)
        calls = mock_execute_query.call_args_list
        # Check first call (user activity)
        self.assertEqual(calls[0][0][1], unittest.mock.ANY) # query string
        self.assertEqual(calls[0][0][2], (guild_id, start_date_str_calc, end_date_str)) # params
        # Check second call (growth)
        self.assertEqual(calls[1][0][1], unittest.mock.ANY) # query string
        self.assertEqual(calls[1][0][2], (guild_id, start_date_str_calc, end_date_str)) # params


if __name__ == '__main__':
    unittest.main()
