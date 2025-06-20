"""
Manages the SQLite database for storing moderation-related data.

This module provides the `ModerationDB` class, which handles schema initialization,
logging of violations, and tracking user violation summaries. It uses `aiosqlite`
for asynchronous database operations.
"""
import aiosqlite
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Any, Dict # Tuple and List not used in this file directly.
import logging

logger = logging.getLogger(__name__)

class ModerationDB:
    """
    Handles database operations for the moderation system using SQLite.
    This includes creating tables, logging moderation actions, and tracking
    user violation histories.
    """
    def __init__(self, db_path: str) -> None:
        """
        Initializes the ModerationDB.

        Args:
            db_path: The file path to the SQLite database.
        """
        self.db_path = db_path

    async def connect(self) -> aiosqlite.Connection:
        """
        Establishes an asynchronous connection to the SQLite database.

        Returns:
            An aiosqlite.Connection object.

        Raises:
            aiosqlite.Error: If connection to the database fails.
        """
        try:
            return await aiosqlite.connect(self.db_path)
        except aiosqlite.Error as e:
            logger.error(f"Database connection error to {self.db_path}: {e}")
            raise # Re-raise to indicate failure to the caller

    async def initialize_schema(self) -> None:
        """
        Initializes the database schema by creating necessary tables if they don't exist.
        This includes 'moderation_logs' and 'user_violations'.
        Logs an error if schema initialization fails.
        """
        try:
            async with await self.connect() as db:
                await db.execute(
                    """
                    CREATE TABLE IF NOT EXISTS moderation_logs (
                        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        message_id TEXT,
                        channel_id TEXT,
                        timestamp DATETIME NOT NULL,
                        violation_type TEXT NOT NULL, -- e.g., 'spam', 'toxicity', 'harassment'
                        rule_name TEXT NOT NULL, -- Specific rule triggered, e.g., 'repeated_text'
                        severity INTEGER,
                        action_taken TEXT, -- e.g., 'warning', 'timeout', 'ban', 'message_deleted'
                        moderator_id TEXT, -- If action was manual or escalated to a human
                        reason TEXT, -- Can store details like matched content or justification
                        duration_seconds INTEGER -- For timeouts
                    )
                    """
                )
                await db.execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_violations (
                        guild_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        violation_count INTEGER DEFAULT 0,
                        last_violation DATETIME,
                        warning_level INTEGER DEFAULT 0,
                        PRIMARY KEY (guild_id, user_id)
                    )
                    """
                )
                await db.commit()
                logger.info(f"Database schema initialized successfully at {self.db_path}")
        except aiosqlite.Error as e:
            logger.error(f"Failed to initialize database schema at {self.db_path}: {e}")
            # Depending on application needs, this might need to be a critical error
            # that stops the bot, or it might be handled more gracefully.

    async def log_violation(
        self,
        guild_id: str,
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    message_id TEXT,
                    channel_id TEXT,
                    timestamp DATETIME NOT NULL,
                    violation_type TEXT NOT NULL, -- e.g., 'spam', 'toxicity', 'harassment'
                    rule_name TEXT NOT NULL, -- Specific rule triggered, e.g., 'repeated_text'
                    severity INTEGER,
                    action_taken TEXT, -- e.g., 'warning', 'timeout', 'ban', 'message_deleted'
                    moderator_id TEXT, -- If action was manual or escalated to a human
                    reason TEXT, -- Can store details like matched content or justification
                    duration_seconds INTEGER -- For timeouts
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS user_violations (
                    guild_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    violation_count INTEGER DEFAULT 0,
                    last_violation DATETIME,
                    warning_level INTEGER DEFAULT 0,
                    PRIMARY KEY (guild_id, user_id)
                )
                """
            )
            await db.commit()

    async def log_violation(
        self,
        guild_id: str,
        user_id: str,
        message_id: Optional[str],
        channel_id: Optional[str], # Added channel_id
        violation_type: str, # This is like the rule category
        rule_name: str,
        severity: int,
        action_taken: str, # String representation of the action
        moderator_id: Optional[str] = None,
        reason: Optional[str] = None, # This will store rule_name + matched_content
        matched_content: Optional[str] = None, # To be part of 'reason'
        duration_seconds: Optional[int] = None, # Added duration
        violation_timestamp: Optional[datetime] = None
    ):
        async with await self.connect() as db:
            vts = violation_timestamp or datetime.now()
            # Construct reason string
            full_reason = f"Rule: {rule_name}"
            if matched_content:
                full_reason += f" - Matched: {matched_content}"
            if reason and reason != full_reason: # If an additional custom reason is provided by caller
                full_reason += f" - Details: {reason}"


            await db.execute(
                """
                INSERT INTO moderation_logs
                (guild_id, user_id, message_id, channel_id, timestamp, violation_type, rule_name, severity, action_taken, moderator_id, reason, duration_seconds)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    guild_id,
                    user_id,
                    message_id,
                    channel_id, # Added
                    vts, # Use provided or current timestamp
                    violation_type,
                    rule_name,
                    severity,
        user_id: str,
        message_id: Optional[str],
        channel_id: Optional[str],
        violation_type: str,
        rule_name: str,
        severity: int,
        action_taken: str,
        moderator_id: Optional[str] = None,
        reason: Optional[str] = None,
        matched_content: Optional[str] = None,
        duration_seconds: Optional[int] = None,
        violation_timestamp: Optional[datetime] = None
    ) -> None:
        """
        Asynchronously logs a moderation violation into the 'moderation_logs' table.

        Args:
            guild_id: ID of the guild.
            user_id: ID of the user who committed the violation.
            message_id: ID of the message that caused the violation.
            channel_id: ID of the channel where the violation occurred.
            violation_type: Category of the violation (e.g., 'Spam').
            rule_name: Specific rule name triggered (e.g., 'repeated_text').
            severity: Severity score of the violation.
            action_taken: String representation of the action taken (e.g., 'warned').
            moderator_id: ID of the moderator, if action was manual.
            reason: Additional details or justification for the log.
            matched_content: Specific content that matched the rule.
            duration_seconds: Duration of the action (e.g., for timeouts).
            violation_timestamp: Specific timestamp of the violation, defaults to now().

        Logs an error if the database operation fails.
        """
        try:
            async with await self.connect() as db:
                vts = violation_timestamp or datetime.now()
                full_reason = f"Rule: {rule_name}"
                if matched_content:
                    full_reason += f" - Matched: {matched_content}"
                if reason and reason != full_reason:
                    full_reason += f" - Details: {reason}"

                await db.execute(
                    """
                    INSERT INTO moderation_logs
                    (guild_id, user_id, message_id, channel_id, timestamp, violation_type, rule_name, severity, action_taken, moderator_id, reason, duration_seconds)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        guild_id, user_id, message_id, channel_id, vts,
                        violation_type, rule_name, severity, action_taken,
                        moderator_id, full_reason, duration_seconds
                    ),
                )
                await db.commit()
        except aiosqlite.Error as e:
            logger.error(f"Failed to log violation for user {user_id} in guild {guild_id}: {e}")


    async def update_user_violation_summary(
        self, guild_id: str, user_id: str, severity_increment: int, violation_timestamp: datetime
    ) -> None:
        """
        Asynchronously updates a user's violation summary in 'user_violations'.
        If the user doesn't exist, a new record is created. Otherwise, the existing
        record's violation_count and warning_level are updated.

        Args:
            guild_id: ID of the guild.
            user_id: ID of the user.
            severity_increment: The severity score of the current violation.
                                Used to determine if warning_level should increase.
            violation_timestamp: Timestamp of the current violation.

        Logs an error if the database operation fails.
        """
        try:
            async with await self.connect() as db:
                async with db.execute("SELECT warning_level FROM user_violations WHERE guild_id = ? AND user_id = ?", (guild_id, user_id)) as cursor:
                    current_row = await cursor.fetchone()

                initial_warning_level_on_insert = 1 if severity_increment >= 5 else 0

                if current_row is None:
                    await db.execute(
                        """
                        INSERT INTO user_violations (guild_id, user_id, violation_count, warning_level, last_violation)
                        VALUES (?, ?, 1, ?, ?)
                        """,
                        (guild_id, user_id, initial_warning_level_on_insert, violation_timestamp),
                    )
                else:
                    current_warning_level = current_row[0]
                    new_warning_level = current_warning_level + (1 if severity_increment >= 5 else 0)

                    await db.execute(
                        """
                        UPDATE user_violations
                        SET violation_count = violation_count + 1,
                            last_violation = ?,
                            warning_level = ?
                        WHERE guild_id = ? AND user_id = ?
                        """,
                        (violation_timestamp, new_warning_level, guild_id, user_id),
                    )
                await db.commit()
        except aiosqlite.Error as e:
            logger.error(f"Failed to update violation summary for user {user_id} in guild {guild_id}: {e}")

    async def get_user_violation_status(self, guild_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Asynchronously retrieves a user's violation status from 'user_violations'.

        Args:
            guild_id: ID of the guild.
            user_id: ID of the user.

        Returns:
            A dictionary containing 'violation_count', 'last_violation',
            and 'warning_level', or None if the user has no record.
            Logs an error and returns None if the database operation fails.
        """
        try:
            async with await self.connect() as db:
                async with db.execute(
                    "SELECT violation_count, last_violation, warning_level FROM user_violations WHERE guild_id = ? AND user_id = ?",
                    (guild_id, user_id),
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        last_violation_dt = None
                        if row[1]:
                            try:
                                last_violation_dt = datetime.fromisoformat(row[1]) if isinstance(row[1], str) else row[1]
                            except ValueError:
                                logger.warning(f"Could not parse last_violation timestamp '{row[1]}' for user {user_id}")

                        return {
                            "violation_count": row[0],
                            "last_violation": last_violation_dt,
                            "warning_level": row[2],
                        }
                    return None
        except aiosqlite.Error as e:
            logger.error(f"Failed to get violation status for user {user_id} in guild {guild_id}: {e}")
            return None

    async def get_total_severity_for_user(
        self, guild_id: str, user_id: str, time_window_hours: int = 24
    ) -> int:
        """
        Asynchronously calculates the total severity of a user's violations
        within a specified time window from 'moderation_logs'.

        Args:
            guild_id: ID of the guild.
            user_id: ID of the user.
            time_window_hours: The lookback period in hours from the current time.

        Returns:
            The sum of severities for violations within the time window.
            Returns 0 if no violations or if a database error occurs.
        """
        try:
            async with await self.connect() as db:
                start_time = datetime.now() - timedelta(hours=time_window_hours)
                async with db.execute(
                    """
                    SELECT SUM(severity)
                    FROM moderation_logs
                    WHERE guild_id = ? AND user_id = ? AND timestamp >= ?
                    """,
                    (guild_id, user_id, start_time),
                ) as cursor:
                    row = await cursor.fetchone()
                    return row[0] if row and row[0] is not None else 0
        except aiosqlite.Error as e:
            logger.error(f"Failed to get total severity for user {user_id} in guild {guild_id}: {e}")
            return 0
