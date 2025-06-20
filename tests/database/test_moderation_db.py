import unittest
import asyncio
import aiosqlite
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

from src.database.moderation_db import ModerationDB

class TestModerationDB(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.db_path = Path("test_moderation_db_isolated.sqlite3")
        # Ensure no old DB file is present
        if self.db_path.exists():
            self.db_path.unlink()
        self.mod_db = ModerationDB(str(self.db_path))
        await self.mod_db.initialize_schema()

    async def asyncTearDown(self):
        # Close any connections if the DB object holds them (not typical for aiosqlite per-method usage)
        # For aiosqlite, connections are typically managed per operation or with a context manager.
        # If ModerationDB.connect() is called in each method and closed (which it is via async with), this is fine.

        # Attempt to clean up the database file
        # This might require ensuring all connections are closed if the DB object itself doesn't manage this globally.
        # Forcibly trying to delete, hoping connections are closed.
        # In a more complex scenario, might need a ModerationDB.close_all_connections() or similar.
        if hasattr(self, 'mod_db') and hasattr(self.mod_db, '_connection') and self.mod_db._connection is not None:
             # If there was a persistent connection object on mod_db (not the case here)
             # await self.mod_db._connection.close()
             # self.mod_db._connection = None
             pass

        if self.db_path.exists():
            try:
                self.db_path.unlink()
            except OSError as e:
                print(f"Error unlinking test DB: {e} - it might still be in use.")


    async def test_log_and_get_status(self):
        ts = datetime.now()
        # Note: The original log_violation didn't have violation_timestamp. Added it in this subtask.
        # Also, added channel_id to log_violation.
        await self.mod_db.log_violation(
            guild_id="g1",
            user_id="u1",
            message_id="m1",
            channel_id="c1",
            violation_type="TestCategory",
            rule_name="TestRule",
            severity=5,
            action_taken="warned",
            reason="test reason",
            # matched_content is part of reason now
            violation_timestamp=ts
        )

        # The update_user_violation_summary logic was adjusted.
        # It now correctly initializes or updates warning_level based on severity_increment.
        await self.mod_db.update_user_violation_summary("g1", "u1", 5, ts)

        status: Optional[Dict[str, Any]] = await self.mod_db.get_user_violation_status("g1", "u1")

        self.assertIsNotNone(status)
        if status: # Satisfy mypy
            self.assertEqual(status['violation_count'], 1)
            # The warning_level logic: initial is 0. If severity_increment >= 5, warning_level becomes 1.
            self.assertEqual(status['warning_level'], 1)
            self.assertIsNotNone(status['last_violation'])
            # Compare timestamps up to seconds, as milliseconds might differ slightly
            self.assertEqual(status['last_violation'].replace(microsecond=0), ts.replace(microsecond=0))

    async def test_get_total_severity_for_user(self):
        now = datetime.now()

        # Logged with explicit timestamps for accurate testing
        await self.mod_db.log_violation("g2", "u2", "m2", "c1", "Cat", "Rule1", 3, "none", violation_timestamp=(now - timedelta(hours=1)))
        await self.mod_db.log_violation("g2", "u2", "m3", "c2", "Cat", "Rule2", 5, "none", violation_timestamp=(now - timedelta(minutes=30)))
        await self.mod_db.log_violation("g2", "u2", "m4", "c3", "Cat", "Rule3", 7, "none", violation_timestamp=(now - timedelta(hours=48))) # Outside 24h window

        total_sev = await self.mod_db.get_total_severity_for_user("g2", "u2", time_window_hours=24)
        self.assertEqual(total_sev, 8) # 3 + 5

    async def test_update_user_violation_summary_increment(self):
        ts1 = datetime.now() - timedelta(minutes=10)
        await self.mod_db.update_user_violation_summary("g3", "u3", 3, ts1) # warning_level should be 0
        status1 = await self.mod_db.get_user_violation_status("g3", "u3")
        self.assertIsNotNone(status1)
        if status1:
            self.assertEqual(status1['violation_count'], 1)
            self.assertEqual(status1['warning_level'], 0)

        ts2 = datetime.now() - timedelta(minutes=5)
        await self.mod_db.update_user_violation_summary("g3", "u3", 6, ts2) # warning_level should increment to 1
        status2 = await self.mod_db.get_user_violation_status("g3", "u3")
        self.assertIsNotNone(status2)
        if status2:
            self.assertEqual(status2['violation_count'], 2)
            self.assertEqual(status2['warning_level'], 1) # 0 + 1 (because severity 6 >= 5)

        ts3 = datetime.now()
        await self.mod_db.update_user_violation_summary("g3", "u3", 2, ts3) # warning_level should stay 1
        status3 = await self.mod_db.get_user_violation_status("g3", "u3")
        self.assertIsNotNone(status3)
        if status3:
            self.assertEqual(status3['violation_count'], 3)
            self.assertEqual(status3['warning_level'], 1) # 1 + 0 (because severity 2 < 5)


    async def test_get_user_violation_status_non_existent(self):
        status = await self.mod_db.get_user_violation_status("non_guild", "non_user")
        self.assertIsNone(status)

    async def test_log_violation_all_fields(self):
        ts = datetime.now()
        await self.mod_db.log_violation(
            guild_id="g4", user_id="u4", message_id="msg1", channel_id="chan1",
            violation_type="Spam", rule_name="Excessive Caps", severity=3,
            action_taken="message_deleted", moderator_id="mod1",
            reason="User posted in all caps.", matched_content="THIS IS ALL CAPS",
            duration_seconds=300, violation_timestamp=ts
        )
        # Verify by fetching (though get_total_severity is simpler here)
        total_sev = await self.mod_db.get_total_severity_for_user("g4", "u4", 1)
        self.assertEqual(total_sev, 3)

        # Check if the log is there by trying to read it directly (simplified check)
        async with self.mod_db.connect() as db:
            async with db.execute("SELECT * FROM moderation_logs WHERE guild_id = 'g4' AND user_id = 'u4'") as cursor:
                log_entry = await cursor.fetchone()
        self.assertIsNotNone(log_entry)
        if log_entry:
            self.assertEqual(log_entry['guild_id'], "g4")
            self.assertEqual(log_entry['user_id'], "u4")
            self.assertEqual(log_entry['message_id'], "msg1")
            self.assertEqual(log_entry['channel_id'], "chan1")
            self.assertEqual(log_entry['violation_type'], "Spam")
            self.assertEqual(log_entry['rule_name'], "Excessive Caps")
            self.assertEqual(log_entry['severity'], 3)
            self.assertEqual(log_entry['action_taken'], "message_deleted")
            self.assertEqual(log_entry['moderator_id'], "mod1")
            self.assertTrue("Rule: Excessive Caps" in log_entry['reason'])
            self.assertTrue("Matched: THIS IS ALL CAPS" in log_entry['reason'])
            self.assertEqual(log_entry['duration_seconds'], 300)
            self.assertEqual(datetime.fromisoformat(log_entry['timestamp']).replace(microsecond=0), ts.replace(microsecond=0))


if __name__ == '__main__':
    unittest.main()
