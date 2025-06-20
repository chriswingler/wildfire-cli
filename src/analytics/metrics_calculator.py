import aiosqlite
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Any

async def _execute_query(db_path: str, query: str, params: tuple = ()) -> List[Tuple[Any, ...]]:
    """
    Private helper to connect to the DB, execute a query, and fetch all results.
    Ensures connections are closed properly.
    """
    try:
        async with aiosqlite.connect(db_path) as db:
            async with db.execute(query, params) as cursor:
                results = await cursor.fetchall()
                return results
    except Exception as e:
        print(f"Database query error: {e}")
        return []

async def get_daily_activity_summary(db_path: str, date_str: str) -> Dict[str, Any]:
    """
    Queries user_analytics and channel_analytics for a given date.
    Returns a dictionary with total messages, reactions, voice minutes,
    and active users for that day.
    Assumes 'active user' means a user with any recorded activity on that day.
    """
    user_query = """
        SELECT SUM(message_count), SUM(reaction_count), SUM(voice_minutes), COUNT(DISTINCT user_id)
        FROM user_analytics
        WHERE date = ?
    """
    # Note: channel_analytics doesn't directly contribute to these specific summary metrics
    # other than potentially message_count, which is already aggregated from user_analytics.
    # Active channels could be a separate metric if needed.

    user_results = await _execute_query(db_path, user_query, (date_str,))

    summary = {
        "date": date_str,
        "total_messages": 0,
        "total_reactions": 0,
        "total_voice_minutes": 0.0, # Ensure float for voice minutes
        "active_users": 0,
    }

    if user_results and user_results[0]:
        messages, reactions, voice_minutes, active_users = user_results[0]
        summary["total_messages"] = messages or 0
        summary["total_reactions"] = reactions or 0
        summary["total_voice_minutes"] = float(voice_minutes or 0.0)
        summary["active_users"] = active_users or 0

    return summary

async def get_activity_summary_period(db_path: str, start_date_str: str, end_date_str: str) -> Dict[str, Any]:
    """
    Aggregates activity data from user_analytics between start_date_str and end_date_str (inclusive).
    Returns a dictionary with total messages, reactions, voice minutes,
    and unique active users over the period.
    """
    query = """
        SELECT SUM(message_count), SUM(reaction_count), SUM(voice_minutes), COUNT(DISTINCT user_id)
        FROM user_analytics
        WHERE date BETWEEN ? AND ?
    """
    results = await _execute_query(db_path, query, (start_date_str, end_date_str))

    summary = {
        "start_date": start_date_str,
        "end_date": end_date_str,
        "total_messages": 0,
        "total_reactions": 0,
        "total_voice_minutes": 0.0,
        "unique_active_users": 0,
    }

    if results and results[0]:
        messages, reactions, voice_minutes, active_users = results[0]
        summary["total_messages"] = messages or 0
        summary["total_reactions"] = reactions or 0
        summary["total_voice_minutes"] = float(voice_minutes or 0.0)
        summary["unique_active_users"] = active_users or 0

    return summary

async def get_user_retention(
    db_path: str, period1_start: str, period1_end: str, period2_start: str, period2_end: str
) -> Dict[str, int]:
    """
    Calculates basic user retention between two periods.
    Counts unique users active in period 1, unique users active in period 2,
    and users active in both periods.
    """
    query_period1_users = "SELECT DISTINCT user_id FROM user_analytics WHERE date BETWEEN ? AND ?"
    query_period2_users = "SELECT DISTINCT user_id FROM user_analytics WHERE date BETWEEN ? AND ?"

    period1_results = await _execute_query(db_path, query_period1_users, (period1_start, period1_end))
    period2_results = await _execute_query(db_path, query_period2_users, (period2_start, period2_end))

    period1_users = {row[0] for row in period1_results}
    period2_users = {row[0] for row in period2_results}

    retained_users = len(period1_users.intersection(period2_users))

    return {
        "period1_active_users": len(period1_users),
        "period2_active_users": len(period2_users),
        "retained_users": retained_users,
    }

async def get_channel_popularity(
    db_path: str, start_date_str: str, end_date_str: str, top_n: int = 10
) -> List[Tuple[str, int]]:
    """
    Gets total message counts per channel within a date range, ordered by popularity.
    Returns a list of tuples: [(channel_id, total_messages), ...].
    """
    query = """
        SELECT channel_id, SUM(message_count) AS total_messages
        FROM channel_analytics
        WHERE date BETWEEN ? AND ?
        GROUP BY channel_id
        ORDER BY total_messages DESC
        LIMIT ?
    """
    results = await _execute_query(db_path, query, (start_date_str, end_date_str, top_n))
    return [(row[0], row[1]) for row in results] if results else []

async def get_peak_activity_days(
    db_path: str, start_date_str: str, end_date_str: str, top_n: int = 5
) -> List[Tuple[str, int]]:
    """
    Finds days with the highest total message count within a given period.
    Returns a list of tuples: [(date, total_messages), ...].
    """
    query = """
        SELECT date, SUM(message_count) AS daily_messages
        FROM user_analytics  -- Could also be channel_analytics if preferred
        WHERE date BETWEEN ? AND ?
        GROUP BY date
        ORDER BY daily_messages DESC
        LIMIT ?
    """
    results = await _execute_query(db_path, query, (start_date_str, end_date_str, top_n))
    return [(row[0], row[1]) for row in results] if results else []
