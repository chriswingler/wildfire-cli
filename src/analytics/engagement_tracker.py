import datetime
from src.database.analytics_db import (
    record_user_activity,
    record_channel_activity,
    record_guild_activity,
)

def _get_date_str(timestamp: datetime.datetime) -> str:
    """Converts a datetime object to a YYYY-MM-DD date string."""
    return timestamp.strftime("%Y-%m-%d")

async def track_message(
    db_path: str,
    guild_id: str,
    user_id: str,
    channel_id: str,
    message_timestamp: datetime.datetime,
):
    """Tracks a message event for user and channel analytics."""
    date_str = _get_date_str(message_timestamp)
    await record_user_activity(
        db_path, guild_id, user_id, date_str, message_count_delta=1
    )
    await record_channel_activity(
        db_path, guild_id, channel_id, date_str, message_count_delta=1
    )
    # Placeholder: Consider if guild_analytics for active members should be updated here
    # or via a separate periodic task.

async def track_reaction(
    db_path: str,
    guild_id: str,
    user_id: str,
    channel_id: str, # Though not stored in user_analytics for reactions, it's usually available
    reaction_timestamp: datetime.datetime,
):
    """Tracks a reaction event for user analytics."""
    date_str = _get_date_str(reaction_timestamp)
    await record_user_activity(
        db_path, guild_id, user_id, date_str, reaction_count_delta=1
    )
    # Note: channel_id is available from reaction events, but not currently
    # stored in user_analytics for reactions. Could be added if schema changes.

async def track_voice_join(
    db_path: str,
    guild_id: str,
    user_id: str,
    channel_id: str,
    join_timestamp: datetime.datetime,
):
    """
    Tracks a voice channel join event.
    This function itself doesn't record to DB directly.
    The calling cog should store the join_timestamp and use it
    with track_voice_leave.
    """
    # Log join for now, actual recording happens on leave.
    print(f"User {user_id} joined voice channel {channel_id} in guild {guild_id} at {join_timestamp}")
    # Placeholder: The cog using this (e.g., WildfireCommands) will need to
    # manage a temporary store of {user_id: join_timestamp}.

async def track_voice_leave(
    db_path: str,
    guild_id: str,
    user_id: str,
    # channel_id: str, # Not strictly needed for user_analytics table
    join_timestamp: datetime.datetime,
    leave_timestamp: datetime.datetime,
):
    """Tracks a voice channel leave event and records voice duration."""
    duration_seconds = (leave_timestamp - join_timestamp).total_seconds()
    voice_minutes_delta = duration_seconds / 60

    # Activity is typically attributed to the date the session ended,
    # or the date it started. Let's use the leave_timestamp's date.
    date_str = _get_date_str(leave_timestamp)

    if voice_minutes_delta > 0: # Only record if duration is positive
        await record_user_activity(
            db_path,
            guild_id,
            user_id,
            date_str,
            voice_minutes_delta=voice_minutes_delta,
        )

# Placeholder for thread and forum engagement tracking:
# async def track_thread_message(db_path, guild_id, user_id, channel_id, thread_id, message_timestamp):
#   """Tracks activity within a thread."""
#   # This might involve checking message.channel type or message.thread property.
#   # Could update user_analytics and potentially a new thread_analytics table.
#   pass

# async def track_forum_post(db_path, guild_id, user_id, channel_id, forum_post_id, post_timestamp):
#   """Tracks creation of a new forum post."""
#   # Similar to threads, would need specific event handlers (e.g., on_thread_create if forums use threads).
#   # Could update user_analytics and potentially a new forum_analytics table.
#   pass
