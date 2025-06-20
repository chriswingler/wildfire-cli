import unittest
from unittest.mock import patch, AsyncMock, call # Added call
from src.database.analytics_db import (
    init_analytics_db,
    record_user_activity,
    record_channel_activity,
    record_guild_activity,
    USER_ANALYTICS_TABLE,
    CHANNEL_ANALYTICS_TABLE,
    GUILD_ANALYTICS_TABLE,
)
from pathlib import Path

class TestAnalyticsDB(unittest.IsolatedAsyncioTestCase):

    @patch('aiosqlite.connect')
    @patch('pathlib.Path.mkdir') # Mock mkdir to avoid actual directory creation
    async def test_init_analytics_db(self, mock_mkdir, mock_connect):
        """Test database initialization creates tables."""
        mock_db_connection = AsyncMock()
        mock_connect.return_value.__aenter__.return_value = mock_db_connection

        db_path = "dummy/path/to/analytics.db"
        await init_analytics_db(db_path)

        # Verify Path.mkdir was called correctly
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

        # Verify connection was made
        mock_connect.assert_called_once_with(Path(db_path))

        # Verify CREATE TABLE statements were executed
        expected_calls = [
            call(USER_ANALYTICS_TABLE),
            call(CHANNEL_ANALYTICS_TABLE),
            call(GUILD_ANALYTICS_TABLE),
        ]
        mock_db_connection.execute.assert_has_calls(expected_calls, any_order=False)
        mock_db_connection.commit.assert_called_once()

    @patch('aiosqlite.connect')
    async def test_record_user_activity(self, mock_connect):
        """Test recording user activity (INSERT OR IGNORE and UPDATE)."""
        mock_db_connection = AsyncMock()
        mock_connect.return_value.__aenter__.return_value = mock_db_connection

        db_path = "dummy.db"
        guild_id = "g1"
        user_id = "u1"
        date_str = "2023-01-01"

        await record_user_activity(db_path, guild_id, user_id, date_str, message_count_delta=1, reaction_count_delta=2, voice_minutes_delta=30)

        expected_calls = [
            call(
                "INSERT OR IGNORE INTO user_analytics (guild_id, user_id, date) VALUES (?, ?, ?)",
                (guild_id, user_id, date_str),
            ),
            call(
                unittest.mock.ANY, # UPDATE query string
                (1, 2, 30, guild_id, user_id, date_str),
            ),
        ]
        mock_db_connection.execute.assert_has_calls(expected_calls, any_order=False)
        # Check the content of the UPDATE query more specifically
        update_query_string = mock_db_connection.execute.call_args_list[1][0][0]
        self.assertIn("UPDATE user_analytics", update_query_string)
        self.assertIn("SET message_count = message_count + ?", update_query_string)
        self.assertIn("reaction_count = reaction_count + ?", update_query_string)
        self.assertIn("voice_minutes = voice_minutes + ?", update_query_string)
        self.assertIn("WHERE guild_id = ? AND user_id = ? AND date = ?", update_query_string)

        mock_db_connection.commit.assert_called_once()

    @patch('aiosqlite.connect')
    async def test_record_channel_activity(self, mock_connect):
        """Test recording channel activity."""
        mock_db_connection = AsyncMock()
        mock_connect.return_value.__aenter__.return_value = mock_db_connection

        db_path = "dummy.db"
        guild_id = "g1"
        channel_id = "c1"
        date_str = "2023-01-01"

        await record_channel_activity(db_path, guild_id, channel_id, date_str, message_count_delta=5, user_count_delta=1)

        expected_calls = [
            call(
                "INSERT OR IGNORE INTO channel_analytics (guild_id, channel_id, date) VALUES (?, ?, ?)",
                (guild_id, channel_id, date_str),
            ),
            call(
                unittest.mock.ANY, # UPDATE query string
                (5, 1, guild_id, channel_id, date_str),
            ),
        ]
        mock_db_connection.execute.assert_has_calls(expected_calls, any_order=False)
        update_query_string = mock_db_connection.execute.call_args_list[1][0][0]
        self.assertIn("UPDATE channel_analytics", update_query_string)
        self.assertIn("SET message_count = message_count + ?", update_query_string)
        self.assertIn("user_count = user_count + ?", update_query_string)
        self.assertIn("WHERE guild_id = ? AND channel_id = ? AND date = ?", update_query_string)

        mock_db_connection.commit.assert_called_once()


    @patch('aiosqlite.connect')
    async def test_record_guild_activity(self, mock_connect):
        """Test recording guild activity."""
        mock_db_connection = AsyncMock()
        mock_connect.return_value.__aenter__.return_value = mock_db_connection

        db_path = "dummy.db"
        guild_id = "g1"
        date_str = "2023-01-01"
        deltas = (10, 2, 1, 0) # total_members, active_members, new_members, left_members

        await record_guild_activity(db_path, guild_id, date_str, *deltas)

        expected_calls = [
            call(
                "INSERT OR IGNORE INTO guild_analytics (guild_id, date) VALUES (?, ?)",
                (guild_id, date_str),
            ),
            call(
                unittest.mock.ANY, # UPDATE query string
                (*deltas, guild_id, date_str),
            ),
        ]
        mock_db_connection.execute.assert_has_calls(expected_calls, any_order=False)
        update_query_string = mock_db_connection.execute.call_args_list[1][0][0]
        self.assertIn("UPDATE guild_analytics", update_query_string)
        self.assertIn("SET total_members = total_members + ?", update_query_string)
        self.assertIn("active_members = active_members + ?", update_query_string)
        self.assertIn("new_members = new_members + ?", update_query_string)
        self.assertIn("left_members = left_members + ?", update_query_string)
        self.assertIn("WHERE guild_id = ? AND date = ?", update_query_string)

        mock_db_connection.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
