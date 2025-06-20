import aiosqlite
import datetime
import os
from pathlib import Path

USER_ANALYTICS_TABLE = """
CREATE TABLE IF NOT EXISTS user_analytics (
    guild_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    date TEXT NOT NULL,
    message_count INTEGER DEFAULT 0,
    reaction_count INTEGER DEFAULT 0,
    voice_minutes INTEGER DEFAULT 0,
    PRIMARY KEY (guild_id, user_id, date)
);
"""

CHANNEL_ANALYTICS_TABLE = """
CREATE TABLE IF NOT EXISTS channel_analytics (
    guild_id TEXT NOT NULL,
    channel_id TEXT NOT NULL,
    date TEXT NOT NULL,
    message_count INTEGER DEFAULT 0,
    user_count INTEGER DEFAULT 0,
    PRIMARY KEY (guild_id, channel_id, date)
);
"""

GUILD_ANALYTICS_TABLE = """
CREATE TABLE IF NOT EXISTS guild_analytics (
    guild_id TEXT NOT NULL,
    date TEXT NOT NULL,
    total_members INTEGER DEFAULT 0,
    active_members INTEGER DEFAULT 0,
    new_members INTEGER DEFAULT 0,
    left_members INTEGER DEFAULT 0,
    PRIMARY KEY (guild_id, date)
);
"""

async def init_analytics_db(db_path: str):
    """Initializes the analytics database with the required tables."""
    try:
        db_path_obj = Path(db_path)
        db_path_obj.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(db_path_obj) as db:
            await db.execute(USER_ANALYTICS_TABLE)
            await db.execute(CHANNEL_ANALYTICS_TABLE)
            await db.execute(GUILD_ANALYTICS_TABLE)
            await db.commit()
        print(f"Analytics database initialized successfully at {db_path}")
    except Exception as e:
        print(f"Error initializing analytics database: {e}")

async def record_user_activity(db_path: str, guild_id: str, user_id: str, date: str, message_count_delta: int = 0, reaction_count_delta: int = 0, voice_minutes_delta: int = 0):
    """Records user activity in the analytics database."""
    try:
        async with aiosqlite.connect(db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO user_analytics (guild_id, user_id, date) VALUES (?, ?, ?)",
                (guild_id, user_id, date),
            )
            await db.execute(
                """
                UPDATE user_analytics
                SET message_count = message_count + ?,
                    reaction_count = reaction_count + ?,
                    voice_minutes = voice_minutes + ?
                WHERE guild_id = ? AND user_id = ? AND date = ?
                """,
                (message_count_delta, reaction_count_delta, voice_minutes_delta, guild_id, user_id, date),
            )
            await db.commit()
    except Exception as e:
        print(f"Error recording user activity: {e}")

async def record_channel_activity(db_path: str, guild_id: str, channel_id: str, date: str, message_count_delta: int = 0, user_count_delta: int = 0):
    """Records channel activity in the analytics database."""
    try:
        async with aiosqlite.connect(db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO channel_analytics (guild_id, channel_id, date) VALUES (?, ?, ?)",
                (guild_id, channel_id, date),
            )
            await db.execute(
                """
                UPDATE channel_analytics
                SET message_count = message_count + ?,
                    user_count = user_count + ?
                WHERE guild_id = ? AND channel_id = ? AND date = ?
                """,
                (message_count_delta, user_count_delta, guild_id, channel_id, date),
            )
            await db.commit()
    except Exception as e:
        print(f"Error recording channel activity: {e}")

async def record_guild_activity(db_path: str, guild_id: str, date: str, total_members_delta: int = 0, active_members_delta: int = 0, new_members_delta: int = 0, left_members_delta: int = 0):
    """Records guild activity in the analytics database."""
    try:
        async with aiosqlite.connect(db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO guild_analytics (guild_id, date) VALUES (?, ?)",
                (guild_id, date),
            )
            await db.execute(
                """
                UPDATE guild_analytics
                SET total_members = total_members + ?,
                    active_members = active_members + ?,
                    new_members = new_members + ?,
                    left_members = left_members + ?
                WHERE guild_id = ? AND date = ?
                """,
                (total_members_delta, active_members_delta, new_members_delta, left_members_delta, guild_id, date),
            )
            await db.commit()
    except Exception as e:
        print(f"Error recording guild activity: {e}")
