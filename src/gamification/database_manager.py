"""
Manages SQLite database operations for gamification statistics.
"""
import aiosqlite
from datetime import datetime

class GamificationDBManager:
    """
    Handles database connections and operations for storing and retrieving
    user gamification statistics (XP, level, etc.).
    """
    def __init__(self, db_path: str):
        """
        Initializes the DBManager with the path to the SQLite database.

        Args:
            db_path: The file path for the SQLite database.
        """
        self.db_path = db_path
        print(f"GamificationDBManager initialized with db_path: {self.db_path}")

    async def init_database(self):
        """
        Initializes the database and creates the user_gamification_stats table
        if it doesn't already exist.
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_gamification_stats (
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 0,
                    message_count INTEGER DEFAULT 0,
                    last_message_timestamp TEXT,
                    PRIMARY KEY (user_id, guild_id)
                )
            """)
            await db.commit()
            print("Database initialized and user_gamification_stats table ensured.")

    async def get_user_stats(self, user_id: int, guild_id: int) -> dict | None:
        """
        Retrieves a user's gamification statistics for a specific guild.

        Args:
            user_id: The Discord user ID.
            guild_id: The Discord guild ID.

        Returns:
            A dictionary containing 'user_id', 'guild_id', 'xp', 'level',
            'message_count', 'last_message_timestamp' if the user is found,
            otherwise None.
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row # Access columns by name
            async with db.execute(
                "SELECT user_id, guild_id, xp, level, message_count, last_message_timestamp FROM user_gamification_stats WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def update_user_stats(
        self, user_id: int, guild_id: int, xp: int, level: int,
        message_count: int, last_message_timestamp: str
    ):
        """
        Updates a user's gamification statistics for a specific guild.
        If the user doesn't exist, a new record is created.

        Args:
            user_id: The Discord user ID.
            guild_id: The Discord guild ID.
            xp: The new total XP for the user.
            level: The new level for the user.
            message_count: The new message count for the user.
            last_message_timestamp: ISO format string of the last message time.
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO user_gamification_stats
                    (user_id, guild_id, xp, level, message_count, last_message_timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, guild_id) DO UPDATE SET
                    xp = excluded.xp,
                    level = excluded.level,
                    message_count = excluded.message_count,
                    last_message_timestamp = excluded.last_message_timestamp
            """, (user_id, guild_id, xp, level, message_count, last_message_timestamp))
            await db.commit()

    async def get_guild_leaderboard(self, guild_id: int, limit: int = 10) -> list[dict]:
        """
        Retrieves the leaderboard for a specific guild, ordered by XP.

        Args:
            guild_id: The Discord guild ID.
            limit: The maximum number of users to return for the leaderboard.

        Returns:
            A list of dictionaries, where each dictionary contains
            'user_id', 'xp', and 'level' for a user on the leaderboard.
        """
        leaderboard_data = []
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row # Access columns by name
            async with db.execute(
                "SELECT user_id, xp, level FROM user_gamification_stats WHERE guild_id = ? ORDER BY xp DESC LIMIT ?",
                (guild_id, limit)
            ) as cursor:
                async for row in cursor:
                    leaderboard_data.append(dict(row))
        return leaderboard_data

    async def get_all_user_stats_for_guild(self, guild_id: int) -> list[dict]:
        """
        Retrieves all user gamification statistics for a specific guild.
        Useful for admin commands or full data exports, but use with caution on large guilds.

        Args:
            guild_id: The Discord guild ID.

        Returns:
            A list of dictionaries, each representing a user's stats in that guild.
        """
        all_stats = []
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT user_id, xp, level, message_count, last_message_timestamp FROM user_gamification_stats WHERE guild_id = ?",
                (guild_id,)
            ) as cursor:
                async for row in cursor:
                    all_stats.append(dict(row))
        return all_stats
