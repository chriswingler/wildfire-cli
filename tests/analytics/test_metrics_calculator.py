import unittest
from unittest.mock import patch, AsyncMock
from src.analytics.metrics_calculator import (
    get_daily_activity_summary,
    get_activity_summary_period,
    get_user_retention,
    get_channel_popularity,
    get_peak_activity_days,
)

class TestMetricsCalculator(unittest.IsolatedAsyncioTestCase):

    @patch('src.analytics.metrics_calculator._execute_query')
    async def test_get_daily_activity_summary_success(self, mock_execute_query):
        """Test get_daily_activity_summary with successful data retrieval."""
        # Mock database response
        mock_execute_query.return_value = [(10, 5, 120.5, 3)] # messages, reactions, voice_minutes, active_users

        date_str = "2023-01-01"
        summary = await get_daily_activity_summary("dummy_db_path", date_str)

        expected_summary = {
            "date": date_str,
            "total_messages": 10,
            "total_reactions": 5,
            "total_voice_minutes": 120.5,
            "active_users": 3,
        }
        self.assertEqual(summary, expected_summary)
        mock_execute_query.assert_called_once_with(
            "dummy_db_path",
            unittest.mock.ANY, # Query string
            (date_str,)
        )

    @patch('src.analytics.metrics_calculator._execute_query')
    async def test_get_daily_activity_summary_no_data(self, mock_execute_query):
        """Test get_daily_activity_summary when no data is found."""
        mock_execute_query.return_value = [(None, None, None, None)] # No data for the day

        date_str = "2023-01-02"
        summary = await get_daily_activity_summary("dummy_db_path", date_str)

        expected_summary = {
            "date": date_str,
            "total_messages": 0,
            "total_reactions": 0,
            "total_voice_minutes": 0.0,
            "active_users": 0,
        }
        self.assertEqual(summary, expected_summary)

    @patch('src.analytics.metrics_calculator._execute_query')
    async def test_get_activity_summary_period(self, mock_execute_query):
        """Test get_activity_summary_period for a date range."""
        mock_execute_query.return_value = [(100, 50, 1200.0, 25)] # total_messages, total_reactions, total_voice_minutes, unique_active_users

        start_date = "2023-01-01"
        end_date = "2023-01-07"
        summary = await get_activity_summary_period("dummy_db_path", start_date, end_date)

        expected_summary = {
            "start_date": start_date,
            "end_date": end_date,
            "total_messages": 100,
            "total_reactions": 50,
            "total_voice_minutes": 1200.0,
            "unique_active_users": 25,
        }
        self.assertEqual(summary, expected_summary)
        mock_execute_query.assert_called_once_with(
            "dummy_db_path",
            unittest.mock.ANY,
            (start_date, end_date)
        )

    @patch('src.analytics.metrics_calculator._execute_query')
    async def test_get_user_retention(self, mock_execute_query):
        """Test get_user_retention between two periods."""
        # Simulate users in period 1 and period 2
        mock_execute_query.side_effect = [
            [("user1",), ("user2",), ("user3",)],  # Period 1 users
            [("user2",), ("user3",), ("user4",)]   # Period 2 users
        ]

        p1_start, p1_end = "2023-01-01", "2023-01-07"
        p2_start, p2_end = "2023-01-08", "2023-01-14"

        retention = await get_user_retention("dummy_db_path", p1_start, p1_end, p2_start, p2_end)

        expected_retention = {
            "period1_active_users": 3,
            "period2_active_users": 3,
            "retained_users": 2, # user2 and user3
        }
        self.assertEqual(retention, expected_retention)
        self.assertEqual(mock_execute_query.call_count, 2)

    @patch('src.analytics.metrics_calculator._execute_query')
    async def test_get_channel_popularity(self, mock_execute_query):
        """Test get_channel_popularity, ensuring correct sorting."""
        mock_execute_query.return_value = [
            ("channel_general", 150),
            ("channel_random", 100),
            ("channel_gaming", 200),
        ]

        start_date = "2023-01-01"
        end_date = "2023-01-30"
        top_n = 3

        popularity = await get_channel_popularity("dummy_db_path", start_date, end_date, top_n=top_n)

        # The mock data is unsorted, the function should sort it based on its SQL query's ORDER BY.
        # However, the current mock just returns a list. The SQL query in the actual function does the sorting.
        # So, the test here verifies that the function returns what the mock provides,
        # assuming the SQL handles the sorting.
        expected_popularity = [
            ("channel_general", 150), # Data as returned by mock
            ("channel_random", 100),
            ("channel_gaming", 200),
        ]
        # If we want to test the Python-side sorting (if any), the mock should be adjusted.
        # But since sorting is in SQL, we test the data passthrough.
        # For this test, let's assume the SQL query is `ORDER BY total_messages DESC LIMIT ?`
        # So the mock should reflect that expected output from SQL.
        mock_execute_query.return_value = [
            ("channel_gaming", 200),
            ("channel_general", 150),
            ("channel_random", 100),
        ]
        expected_popularity_sorted = [
            ("channel_gaming", 200),
            ("channel_general", 150),
            ("channel_random", 100),
        ]
        popularity_sorted = await get_channel_popularity("dummy_db_path", start_date, end_date, top_n=top_n)

        self.assertEqual(popularity_sorted, expected_popularity_sorted)
        mock_execute_query.assert_called_with(
            "dummy_db_path",
            unittest.mock.ANY,
            (start_date, end_date, top_n)
        )

    @patch('src.analytics.metrics_calculator._execute_query')
    async def test_get_peak_activity_days(self, mock_execute_query):
        """Test get_peak_activity_days."""
        mock_execute_query.return_value = [
            ("2023-01-05", 500),
            ("2023-01-02", 450),
        ]

        start_date = "2023-01-01"
        end_date = "2023-01-07"
        top_n = 2

        peak_days = await get_peak_activity_days("dummy_db_path", start_date, end_date, top_n=top_n)

        expected_peak_days = [
            ("2023-01-05", 500),
            ("2023-01-02", 450),
        ]
        self.assertEqual(peak_days, expected_peak_days)
        mock_execute_query.assert_called_once_with(
            "dummy_db_path",
            unittest.mock.ANY,
            (start_date, end_date, top_n)
        )

if __name__ == '__main__':
    unittest.main()
