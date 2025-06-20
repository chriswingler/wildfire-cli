# Unit tests for GamificationDBManager
import pytest
import pytest_asyncio # For async fixtures
import aiosqlite
from datetime import datetime
from src.gamification.database_manager import GamificationDBManager

@pytest_asyncio.fixture # Use pytest_asyncio.fixture for async fixtures
async def db_manager() -> GamificationDBManager:
    """
    Provides an in-memory GamificationDBManager instance with an initialized database
    for each test function.
    """
    manager = GamificationDBManager(":memory:")
    await manager.init_database() # Ensure table is created
    return manager

@pytest.mark.asyncio
async def test_init_database_creates_table(db_manager: GamificationDBManager):
    """Test that init_database actually creates the table."""
    async with aiosqlite.connect(db_manager.db_path) as db:
        async with db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='user_gamification_stats'"
        ) as cursor:
            result = await cursor.fetchone()
            assert result is not None, "Table 'user_gamification_stats' was not created."
            assert result[0] == "user_gamification_stats"

@pytest.mark.asyncio
async def test_get_user_stats_non_existent(db_manager: GamificationDBManager):
    """Test retrieving stats for a user that does not exist."""
    stats = await db_manager.get_user_stats(user_id=1, guild_id=1)
    assert stats is None

@pytest.mark.asyncio
async def test_update_and_get_user_stats_new_user(db_manager: GamificationDBManager):
    """Test adding a new user's stats and then retrieving them."""
    user_id = 10
    guild_id = 1
    xp = 100
    level = 2
    message_count = 5
    timestamp = datetime.now().isoformat()

    await db_manager.update_user_stats(user_id, guild_id, xp, level, message_count, timestamp)

    stats = await db_manager.get_user_stats(user_id, guild_id)
    assert stats is not None
    assert stats['user_id'] == user_id
    assert stats['guild_id'] == guild_id
    assert stats['xp'] == xp
    assert stats['level'] == level
    assert stats['message_count'] == message_count
    assert stats['last_message_timestamp'] == timestamp

@pytest.mark.asyncio
async def test_update_user_stats_existing_user(db_manager: GamificationDBManager):
    """Test updating an existing user's stats."""
    user_id = 20
    guild_id = 1
    timestamp_initial = datetime.now().isoformat()

    # Initial insert
    await db_manager.update_user_stats(user_id, guild_id, 50, 1, 2, timestamp_initial)

    # Update
    new_xp = 150
    new_level = 3
    new_message_count = 10
    timestamp_updated = datetime.now().isoformat()
    await db_manager.update_user_stats(user_id, guild_id, new_xp, new_level, new_message_count, timestamp_updated)

    stats = await db_manager.get_user_stats(user_id, guild_id)
    assert stats is not None
    assert stats['xp'] == new_xp
    assert stats['level'] == new_level
    assert stats['message_count'] == new_message_count
    assert stats['last_message_timestamp'] == timestamp_updated

@pytest.mark.asyncio
async def test_get_guild_leaderboard_empty(db_manager: GamificationDBManager):
    """Test retrieving leaderboard from an empty database for a guild."""
    leaderboard = await db_manager.get_guild_leaderboard(guild_id=1, limit=10)
    assert isinstance(leaderboard, list)
    assert len(leaderboard) == 0

@pytest.mark.asyncio
async def test_get_guild_leaderboard_single_guild(db_manager: GamificationDBManager):
    """Test leaderboard for a single guild with multiple users."""
    guild_id = 100
    users_data = [
        (1, guild_id, 100, 2, 5, datetime.now().isoformat()), # user_id, guild_id, xp, level, msg_count, timestamp
        (2, guild_id, 200, 3, 10, datetime.now().isoformat()),
        (3, guild_id, 50, 1, 2, datetime.now().isoformat()),
        (4, guild_id, 150, 2, 7, datetime.now().isoformat()),
    ]
    for data in users_data:
        await db_manager.update_user_stats(*data)

    leaderboard = await db_manager.get_guild_leaderboard(guild_id, limit=10)

    assert len(leaderboard) == 4
    # Verify order (highest XP first)
    assert leaderboard[0]['user_id'] == 2 # 200 XP
    assert leaderboard[0]['xp'] == 200
    assert leaderboard[0]['level'] == 3

    assert leaderboard[1]['user_id'] == 4 # 150 XP
    assert leaderboard[1]['xp'] == 150

    assert leaderboard[2]['user_id'] == 1 # 100 XP
    assert leaderboard[2]['xp'] == 100

    assert leaderboard[3]['user_id'] == 3 # 50 XP
    assert leaderboard[3]['xp'] == 50

@pytest.mark.asyncio
async def test_get_guild_leaderboard_limit(db_manager: GamificationDBManager):
    """Test that the limit parameter in get_guild_leaderboard is respected."""
    guild_id = 200
    for i in range(15): # Insert 15 users
        await db_manager.update_user_stats(i, guild_id, (i + 1) * 10, i // 5 + 1, i * 2, datetime.now().isoformat())

    leaderboard_limit_5 = await db_manager.get_guild_leaderboard(guild_id, limit=5)
    assert len(leaderboard_limit_5) == 5

    leaderboard_limit_10 = await db_manager.get_guild_leaderboard(guild_id, limit=10)
    assert len(leaderboard_limit_10) == 10

    # Check if the top user is correct (user 14 with 150 XP)
    assert leaderboard_limit_5[0]['user_id'] == 14
    assert leaderboard_limit_5[0]['xp'] == 150

@pytest.mark.asyncio
async def test_get_guild_leaderboard_multiple_guilds(db_manager: GamificationDBManager):
    """Test that leaderboard correctly isolates data by guild_id."""
    guild1_id = 301
    guild2_id = 302

    # Guild 1 data
    await db_manager.update_user_stats(1, guild1_id, 100, 2, 5, datetime.now().isoformat())
    await db_manager.update_user_stats(2, guild1_id, 200, 3, 10, datetime.now().isoformat())

    # Guild 2 data
    await db_manager.update_user_stats(3, guild2_id, 150, 2, 7, datetime.now().isoformat())
    await db_manager.update_user_stats(4, guild2_id, 50, 1, 3, datetime.now().isoformat())

    leaderboard_g1 = await db_manager.get_guild_leaderboard(guild1_id, limit=10)
    assert len(leaderboard_g1) == 2
    assert leaderboard_g1[0]['user_id'] == 2 # User 2 has 200 XP in Guild 1
    assert leaderboard_g1[1]['user_id'] == 1 # User 1 has 100 XP in Guild 1

    leaderboard_g2 = await db_manager.get_guild_leaderboard(guild2_id, limit=10)
    assert len(leaderboard_g2) == 2
    assert leaderboard_g2[0]['user_id'] == 3 # User 3 has 150 XP in Guild 2
    assert leaderboard_g2[1]['user_id'] == 4 # User 4 has 50 XP in Guild 2

@pytest.mark.asyncio
async def test_get_all_user_stats_for_guild(db_manager: GamificationDBManager):
    """Test retrieving all user stats for a specific guild."""
    guild_id = 400
    num_users = 5
    users_data = []
    for i in range(num_users):
        data = (i, guild_id, (i+1)*10, i, (i+1)*2, datetime.now().isoformat())
        users_data.append(data)
        await db_manager.update_user_stats(*data)

    # Add a user to another guild to ensure it's not fetched
    await db_manager.update_user_stats(99, guild_id + 1, 100, 1, 1, datetime.now().isoformat())

    all_stats = await db_manager.get_all_user_stats_for_guild(guild_id)
    assert len(all_stats) == num_users

    # Verify content (optional, but good for one entry)
    # Sort by user_id for deterministic comparison if needed
    all_stats_sorted = sorted(all_stats, key=lambda x: x['user_id'])

    for i in range(num_users):
        assert all_stats_sorted[i]['user_id'] == users_data[i][0]
        assert all_stats_sorted[i]['xp'] == users_data[i][2]
        assert all_stats_sorted[i]['level'] == users_data[i][3]
        assert all_stats_sorted[i]['message_count'] == users_data[i][4]
        assert all_stats_sorted[i]['last_message_timestamp'] == users_data[i][5]

@pytest.mark.asyncio
async def test_get_all_user_stats_for_guild_empty(db_manager: GamificationDBManager):
    """Test retrieving all user stats for a guild with no users."""
    all_stats = await db_manager.get_all_user_stats_for_guild(guild_id=401)
    assert isinstance(all_stats, list)
    assert len(all_stats) == 0
