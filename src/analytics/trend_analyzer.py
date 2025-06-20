import aiosqlite
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Any, Optional

# This helper can be refactored into a shared utility if used by more modules.
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
        print(f"Database query error in trend_analyzer: {e}")
        return []

async def get_sentiment_trend(
    db_path: str, start_date_str: str, end_date_str: str
) -> List[Tuple[str, float]]:
    """
    **PLACEHOLDER FUNCTION**
    Simulates fetching sentiment trend data. Actual implementation would require
    LLM-based sentiment analysis of messages, which is out of scope for the initial build.
    Currently returns a mock trend or an empty list.
    The schema `channel_analytics` has an `avg_sentiment` column for this.
    """
    # Mock implementation:
    print(f"Fetching mock sentiment trend for {db_path} from {start_date_str} to {end_date_str}")
    # query = "SELECT date, avg_sentiment FROM channel_analytics WHERE date BETWEEN ? AND ? ORDER BY date;"
    # results = await _execute_query(db_path, query, (start_date_str, end_date_str))
    # return [(row[0], float(row[1])) for row in results if row[1] is not None]

    # Example mock data:
    mock_data = []
    current_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    mock_sentiment = 0.5
    while current_date <= end_date:
        mock_data.append((current_date.strftime("%Y-%m-%d"), round(mock_sentiment, 2)))
        mock_sentiment += 0.05 # Simulate some change
        if mock_sentiment > 1.0: mock_sentiment = 0.0
        current_date += timedelta(days=1)
    return mock_data

async def get_topic_trends(
    db_path: str, start_date_str: str, end_date_str: str
) -> List[Dict[str, Any]]:
    """
    **PLACEHOLDER FUNCTION**
    Simulates fetching topic trends. Actual implementation would require
    NLP/LLM-based topic modeling of messages, which is complex and out of scope.
    Currently returns a mock list of topics or an empty list.
    """
    print(f"Fetching mock topic trends for {db_path} from {start_date_str} to {end_date_str}")
    # No specific schema column for this yet. Would likely be a separate table.
    # Example mock data:
    return [
        {"topic": "Wildfires", "urgency": "High", "mentions_over_time": [(start_date_str, 10), (end_date_str, 25)]},
        {"topic": "Resource Allocation", "urgency": "Medium", "mentions_over_time": [(start_date_str, 5), (end_date_str, 15)]},
    ]

async def get_community_growth_patterns(
    db_path: str, start_date_str: str, end_date_str: str
) -> List[Tuple[str, int, int, int]]:
    """
    Queries guild_analytics for total_members, new_members, and left_members
    over the specified period.
    Returns a list of tuples: [(date, total_members, new_members, left_members), ...].
    """
    query = """
        SELECT date, total_members, new_members, left_members
        FROM guild_analytics
        WHERE date BETWEEN ? AND ?
        ORDER BY date;
    """
    results = await _execute_query(db_path, query, (start_date_str, end_date_str))
    return [(row[0], int(row[1]), int(row[2]), int(row[3])) for row in results]

async def calculate_engagement_quality_score(
    db_path: str, user_id: str, end_date_str: str, lookback_days: int = 30
) -> float:
    """
    Calculates a simple formula-based engagement quality score for a user.
    Score = (message_count * 0.5) + (reaction_count * 0.3) + (voice_minutes * 0.2).
    Returns a single float score. If no activity, score is 0.
    """
    try:
        end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
        start_dt = end_dt - timedelta(days=lookback_days -1) # -1 to make it inclusive of end_date_str for 30 days
        start_date_str_calc = start_dt.strftime("%Y-%m-%d")
    except ValueError:
        print(f"Invalid date format for end_date_str: {end_date_str}")
        return 0.0

    query = """
        SELECT SUM(message_count), SUM(reaction_count), SUM(voice_minutes)
        FROM user_analytics
        WHERE user_id = ? AND date BETWEEN ? AND ?;
    """
    results = await _execute_query(db_path, query, (user_id, start_date_str_calc, end_date_str))

    if not results or results[0] is None:
        return 0.0

    msg_count, react_count, voice_mins = results[0]
    msg_count = msg_count or 0
    react_count = react_count or 0
    voice_mins = voice_mins or 0.0

    score = (msg_count * 0.5) + (react_count * 0.3) + (float(voice_mins) * 0.2)
    return round(score, 2)

async def calculate_community_health_score(
    db_path: str, guild_id: str, end_date_str: str, lookback_days: int = 30
) -> float:
    """
    Calculates a basic composite community health score for a guild.
    This is a simplified metric and can be expanded.
    Factors considered:
    1. Activity Volume (total messages)
    2. Engagement (total reactions)
    3. Active Users (count of distinct users)
    4. Net Member Growth (new members - left members)
    Each factor is normalized to a scale (e.g., 0-1) if possible, then weighted.
    For now, using raw sums and a simple weighting. Max score ~100.
    """
    try:
        end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
        start_dt = end_dt - timedelta(days=lookback_days -1)
        start_date_str_calc = start_dt.strftime("%Y-%m-%d")
    except ValueError:
        print(f"Invalid date format for end_date_str: {end_date_str}")
        return 0.0

    # 1. Activity Volume (messages)
    user_activity_query = """
        SELECT SUM(message_count), SUM(reaction_count), COUNT(DISTINCT user_id)
        FROM user_analytics
        WHERE guild_id = ? AND date BETWEEN ? AND ?;
    """
    user_activity_res = await _execute_query(db_path, user_activity_query, (guild_id, start_date_str_calc, end_date_str))

    total_messages = 0
    total_reactions = 0
    distinct_users = 0
    if user_activity_res and user_activity_res[0]:
        total_messages = user_activity_res[0][0] or 0
        total_reactions = user_activity_res[0][1] or 0
        distinct_users = user_activity_res[0][2] or 0

    # 2. Growth Metrics
    growth_query = """
        SELECT SUM(new_members), SUM(left_members)
        FROM guild_analytics
        WHERE guild_id = ? AND date BETWEEN ? AND ?;
    """
    growth_res = await _execute_query(db_path, growth_query, (guild_id, start_date_str_calc, end_date_str))

    new_members = 0
    left_members = 0
    if growth_res and growth_res[0]:
        new_members = growth_res[0][0] or 0
        left_members = growth_res[0][1] or 0

    net_growth = new_members - left_members

    # Simple weighted score (highly subjective, weights can be tuned)
    # Max possible for each component (approx):
    # messages_score: ~50 (e.g. 1000 messages * 0.05)
    # reactions_score: ~30 (e.g. 600 reactions * 0.05)
    # active_users_score: ~10 (e.g. 20 users * 0.5)
    # net_growth_score: ~10 (e.g. 10 net new * 1)

    messages_score = min(total_messages * 0.02, 40) # Cap at 40
    reactions_score = min(total_reactions * 0.03, 30) # Cap at 30
    active_users_score = min(distinct_users * 0.5, 20) # Cap at 20
    net_growth_score = max(min(net_growth * 1, 10), -10) # Cap at 10, allow negative impact

    community_health = messages_score + reactions_score + active_users_score + net_growth_score
    return round(max(0, min(community_health, 100)), 2) # Ensure score is between 0 and 100.
