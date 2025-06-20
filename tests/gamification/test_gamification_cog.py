# Unit tests for GamificationCog
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import discord # Import discord for type hinting and errors, but avoid direct use where possible for unit tests.
from discord.ext import commands

# Modules to be tested
from src.cogs.gamification_cog import GamificationCog
from src.gamification.xp_calculator import XPCalculator
from src.gamification.level_manager import LevelManager
from src.gamification.contribution_analyzer import ContributionAnalyzer
# GamificationDBManager is mocked, so direct import might not be needed if fully mocked.
# from src.gamification.database_manager import GamificationDBManager


# --- Fixtures ---
@pytest.fixture
def mock_bot() -> MagicMock:
    """Fixture for a mocked Discord bot instance."""
    bot = MagicMock(spec=commands.Bot)
    bot.user = MagicMock(spec=discord.ClientUser)
    bot.user.id = 1234567890  # Example bot user ID
    return bot

@pytest.fixture
def mock_db_manager() -> AsyncMock:
    """Fixture for a mocked GamificationDBManager."""
    db_m = AsyncMock()
    # Default return for get_user_stats for a new user
    db_m.get_user_stats.return_value = None
    return db_m

@pytest_asyncio.fixture # Use pytest_asyncio.fixture for async fixtures
async def gamification_cog(mock_bot: MagicMock, mock_db_manager: AsyncMock) -> GamificationCog:
    """Fixture for GamificationCog with mocked dependencies."""
    # Temporarily patch the GamificationDBManager during cog instantiation
    with patch('src.cogs.gamification_cog.GamificationDBManager', return_value=mock_db_manager):
        cog = GamificationCog(bot=mock_bot)
        # Normally cog_load is called by discord.py, we call it manually for tests
        # if it contains critical async setup like db_manager.init_database()
        await cog.cog_load() # This will call mock_db_manager.init_database()
    return cog

@pytest.fixture
def mock_guild() -> MagicMock:
    """Fixture for a mocked Discord Guild."""
    guild = MagicMock(spec=discord.Guild)
    guild.id = 1000 # Example Guild ID
    guild.name = "Test Guild"
    guild.roles = [] # Start with no roles, can be populated by tests

    # Mock discord.utils.get for role fetching within the guild context
    def mock_utils_get(iterable, **attrs):
        name_to_find = attrs.get('name')
        for role in iterable: # iterable here would be guild.roles
            if role.name == name_to_find:
                return role
        return None
    guild.utils_get = MagicMock(side_effect=mock_utils_get) # Attach to guild for easy access in tests
    # If discord.utils.get is used directly in cog, patch it globally:
    # @patch('discord.utils.get', side_effect=mock_utils_get_global)
    return guild

@pytest.fixture
def mock_member(mock_guild: MagicMock) -> MagicMock:
    """Fixture for a mocked Discord Member."""
    member = MagicMock(spec=discord.Member)
    member.id = 2000 # Example Member ID
    member.name = "TestUser"
    member.display_name = "TestUser"
    member.bot = False
    member.guild = mock_guild
    member.roles = [] # Start with no roles
    member.mention = f"<@{member.id}>"
    member.add_roles = AsyncMock()
    member.remove_roles = AsyncMock()
    member.display_avatar = MagicMock()
    member.display_avatar.url = "http://example.com/avatar.png"
    member.color = discord.Color.default()
    return member

@pytest.fixture
def mock_message(mock_member: MagicMock, mock_guild: MagicMock) -> MagicMock:
    """Fixture for a mocked Discord Message."""
    message = MagicMock(spec=discord.Message)
    message.author = mock_member
    message.guild = mock_guild
    message.channel = AsyncMock(spec=discord.TextChannel) # Mock channel with send
    message.channel.id = 3000 # Example Channel ID
    message.content = "This is a test message."
    return message

@pytest.fixture
def mock_interaction(mock_member: MagicMock, mock_guild: MagicMock) -> AsyncMock:
    interaction = AsyncMock(spec=discord.Interaction)
    interaction.user = mock_member
    interaction.guild = mock_guild
    interaction.guild_id = mock_guild.id
    interaction.response = AsyncMock(spec=discord.InteractionResponse)
    interaction.channel = AsyncMock(spec=discord.TextChannel)
    return interaction


# --- Tests for on_message ---
@pytest.mark.asyncio
async def test_on_message_bot_author_ignored(gamification_cog: GamificationCog, mock_message: MagicMock):
    """Test that messages from bots are ignored."""
    mock_message.author.bot = True
    await gamification_cog.on_message(mock_message)
    gamification_cog.contribution_analyzer.analyze_contribution.assert_not_called()
    gamification_cog.db_manager.get_user_stats.assert_not_called()

@pytest.mark.asyncio
async def test_on_message_dm_ignored(gamification_cog: GamificationCog, mock_message: MagicMock):
    """Test that DM messages are ignored."""
    mock_message.guild = None
    await gamification_cog.on_message(mock_message)
    gamification_cog.contribution_analyzer.analyze_contribution.assert_not_called()

@pytest.mark.asyncio
async def test_on_message_xp_gain_no_level_up(gamification_cog: GamificationCog, mock_message: MagicMock, mock_db_manager: AsyncMock):
    """Test XP gain without a level up."""
    # Setup mocks
    mock_db_manager.get_user_stats.return_value = {'user_id': mock_message.author.id, 'guild_id': mock_message.guild.id, 'xp': 0, 'level': 0, 'message_count': 0}
    gamification_cog.contribution_analyzer.analyze_contribution.return_value = {
        'is_helpful_answer': True # Enough for some XP
    }

    expected_xp = XPCalculator.BASE_MESSAGE_XP + XPCalculator.HELPFUL_ANSWER_XP

    await gamification_cog.on_message(mock_message)

    # Assertions
    gamification_cog.db_manager.update_user_stats.assert_called_once()
    args, _ = gamification_cog.db_manager.update_user_stats.call_args
    # args = (user_id, guild_id, xp, level, message_count, timestamp_str)
    assert args[0] == mock_message.author.id
    assert args[1] == mock_message.guild.id
    assert args[2] == expected_xp # New total XP
    assert args[3] == gamification_cog.level_manager.get_level_for_xp(expected_xp) # Expected new level
    assert args[4] == 1 # New message count

    mock_message.channel.send.assert_not_called() # No level up message

@pytest.mark.asyncio
async def test_on_message_level_up_no_role_change(gamification_cog: GamificationCog, mock_message: MagicMock, mock_db_manager: AsyncMock):
    """Test XP gain with a level up, but no change in role tier."""
    initial_xp = gamification_cog.level_manager.get_xp_for_level(1) # Starts at level 1
    initial_level = 1
    # XP needed for level 2 is 283. XP for level 1 is 100.
    # To level up to 2, user needs 283-initial_xp more.
    # Let's make them earn enough to get to level 2 (from level 1)
    # Current config: L1 -> "Community Member", L11 -> "Active Contributor"
    # So level 1 to level 2 is still "Community Member"

    mock_db_manager.get_user_stats.return_value = {
        'user_id': mock_message.author.id,
        'guild_id': mock_message.guild.id,
        'xp': initial_xp,
        'level': initial_level,
        'message_count': 5
    }
    # Grant enough XP to level up to level 2 or 3, but not 11
    # Level 2 needs 283 XP. Level 3 needs 520 XP.
    # If current_xp = 100 (L1), earn 200 XP -> 300 XP (L2)
    earned_xp_from_message = 200
    # Mock analyze_contribution to return a high XP value indirectly
    # This is a bit tricky as calculate_xp sums constants. Let's assume it can return a value.
    gamification_cog.xp_calculator.calculate_xp = MagicMock(return_value=earned_xp_from_message)

    await gamification_cog.on_message(mock_message)

    new_total_xp = initial_xp + earned_xp_from_message
    new_expected_level = gamification_cog.level_manager.get_level_for_xp(new_total_xp)

    assert new_expected_level > initial_level # Ensure level up occurred

    gamification_cog.db_manager.update_user_stats.assert_called_once()
    args, _ = gamification_cog.db_manager.update_user_stats.call_args
    assert args[2] == new_total_xp
    assert args[3] == new_expected_level

    mock_message.channel.send.assert_called_once() # Level up message
    # Role change logic assertions (add_roles/remove_roles should NOT be called)
    mock_message.author.add_roles.assert_not_called()
    mock_message.author.remove_roles.assert_not_called()


@pytest.mark.asyncio
async def test_on_message_level_up_with_role_change(gamification_cog: GamificationCog, mock_message: MagicMock, mock_guild: MagicMock, mock_member: MagicMock, mock_db_manager: AsyncMock):
    """Test level up that results in a new role assignment and old role removal."""
    # User is level 10 ("Community Member"), will level up to 11 ("Active Contributor")
    initial_level = 10
    initial_xp = gamification_cog.level_manager.get_xp_for_level(initial_level) # XP for L10 is 3162

    mock_db_manager.get_user_stats.return_value = {
        'user_id': mock_member.id, 'guild_id': mock_guild.id,
        'xp': initial_xp, 'level': initial_level, 'message_count': 10
    }

    # XP for L11 is 3642. Need 3642 - 3162 = 480 XP to level up.
    # Let's make the message earn 500 XP.
    earned_xp_from_message = 500
    gamification_cog.xp_calculator.calculate_xp = MagicMock(return_value=earned_xp_from_message)

    # Setup roles on guild and member
    old_role_name = "Community Member" # Role for level 1-10
    new_role_name = "Active Contributor" # Role for level 11-25

    mock_old_role = MagicMock(spec=discord.Role); mock_old_role.name = old_role_name; mock_old_role.id = 1
    mock_new_role = MagicMock(spec=discord.Role); mock_new_role.name = new_role_name; mock_new_role.id = 2

    mock_guild.roles = [mock_old_role, mock_new_role]
    mock_member.roles = [mock_old_role] # Member has the old role

    # Patch discord.utils.get used by the cog
    with patch('discord.utils.get', side_effect=lambda iterable, name: next((r for r in iterable if r.name == name), None)):
        await gamification_cog.on_message(mock_message)

    new_total_xp = initial_xp + earned_xp_from_message # 3162 + 500 = 3662
    new_expected_level = gamification_cog.level_manager.get_level_for_xp(new_total_xp) # Should be 11

    assert new_expected_level == 11
    mock_message.channel.send.assert_called_once() # Level up message

    # Role change assertions
    mock_member.remove_roles.assert_called_once_with(mock_old_role, reason="Level up, new role tier assigned")
    mock_member.add_roles.assert_called_once_with(mock_new_role, reason="Level up achievement")


# --- Tests for Slash Commands (Simplified) ---

@pytest.mark.asyncio
async def test_level_command_self(gamification_cog: GamificationCog, mock_interaction: AsyncMock, mock_db_manager: AsyncMock):
    """Test /level command for the invoking user."""
    user_data = {'user_id': mock_interaction.user.id, 'guild_id': mock_interaction.guild_id, 'xp': 150, 'level': 1, 'message_count': 5}
    mock_db_manager.get_user_stats.return_value = user_data

    # Mock the helper directly as its output is what we care about for the command
    expected_embed = discord.Embed(title="Your Level & Progress") # Simplified
    gamification_cog._generate_level_progress_embed = AsyncMock(return_value=expected_embed)

    await gamification_cog.level_command.callback(gamification_cog, mock_interaction, user=None)

    gamification_cog._generate_level_progress_embed.assert_called_once_with(mock_interaction, mock_interaction.user, is_self_command=True)
    mock_interaction.response.send_message.assert_called_once_with(embed=expected_embed)

@pytest.mark.asyncio
async def test_level_command_other_user(gamification_cog: GamificationCog, mock_interaction: AsyncMock, mock_member: MagicMock, mock_db_manager: AsyncMock):
    """Test /level command for another user."""
    other_user_mock = mock_member # Use the general member fixture
    user_data = {'user_id': other_user_mock.id, 'guild_id': mock_interaction.guild_id, 'xp': 200, 'level': 2, 'message_count': 10}
    mock_db_manager.get_user_stats.return_value = user_data

    expected_embed = discord.Embed(title=f"Level Information for {other_user_mock.display_name}") # Simplified
    gamification_cog._generate_level_progress_embed = AsyncMock(return_value=expected_embed)

    await gamification_cog.level_command.callback(gamification_cog, mock_interaction, user=other_user_mock)

    gamification_cog._generate_level_progress_embed.assert_called_once_with(mock_interaction, other_user_mock, is_self_command=False)
    mock_interaction.response.send_message.assert_called_once_with(embed=expected_embed)

@pytest.mark.asyncio
async def test_progress_command(gamification_cog: GamificationCog, mock_interaction: AsyncMock, mock_db_manager: AsyncMock):
    """Test /progress command."""
    user_data = {'user_id': mock_interaction.user.id, 'guild_id': mock_interaction.guild_id, 'xp': 150, 'level': 1, 'message_count': 5}
    mock_db_manager.get_user_stats.return_value = user_data

    expected_embed = discord.Embed(title="Your Level & Progress") # Simplified
    gamification_cog._generate_level_progress_embed = AsyncMock(return_value=expected_embed)

    await gamification_cog.progress_command.callback(gamification_cog, mock_interaction)

    gamification_cog._generate_level_progress_embed.assert_called_once_with(mock_interaction, mock_interaction.user, is_self_command=True)
    mock_interaction.response.send_message.assert_called_once_with(embed=expected_embed)


@pytest.mark.asyncio
async def test_leaderboard_command(gamification_cog: GamificationCog, mock_interaction: AsyncMock, mock_guild: MagicMock, mock_db_manager: AsyncMock):
    """Test /leaderboard command."""
    leaderboard_db_return = [
        {'user_id': 2000, 'xp': 500, 'level': 5}, # Corresponds to mock_interaction.user / mock_member
        {'user_id': 3000, 'xp': 400, 'level': 4},
    ]
    mock_db_manager.get_guild_leaderboard.return_value = leaderboard_db_return

    # Mock guild.get_member behavior
    user_map = {
        2000: mock_interaction.user, # mock_member from fixture
        3000: MagicMock(spec=discord.Member, id=3000, display_name="User3000", guild=mock_guild)
    }
    mock_guild.get_member.side_effect = lambda user_id: user_map.get(user_id)

    await gamification_cog.leaderboard_command.callback(gamification_cog, mock_interaction, timeframe="all_time")

    mock_db_manager.get_guild_leaderboard.assert_called_once_with(mock_interaction.guild.id, limit=10)
    mock_interaction.response.send_message.assert_called_once()
    args, kwargs = mock_interaction.response.send_message.call_args
    sent_embed = kwargs['embed']
    assert "XP Leaderboard" in sent_embed.title
    assert "TestUser - Level 5 (500 XP)" in sent_embed.description # From mock_member
    assert "User3000 - Level 4 (400 XP)" in sent_embed.description


@pytest.mark.asyncio
async def test_contributions_command_self(gamification_cog: GamificationCog, mock_interaction: AsyncMock, mock_db_manager: AsyncMock):
    """Test /contributions command for self."""
    user_data = {'user_id': mock_interaction.user.id, 'guild_id': mock_interaction.guild_id,
                   'xp': 180, 'level': 1, 'message_count': 12}
    mock_db_manager.get_user_stats.return_value = user_data
    gamification_cog.get_role_name_for_level = MagicMock(return_value="Community Member") # Mock this helper

    await gamification_cog.contributions_command.callback(gamification_cog, mock_interaction, user=None)

    mock_db_manager.get_user_stats.assert_called_once_with(mock_interaction.user.id, mock_interaction.guild.id)
    mock_interaction.response.send_message.assert_called_once()
    args, kwargs = mock_interaction.response.send_message.call_args
    sent_embed = kwargs['embed']
    assert f"Contribution Summary for {mock_interaction.user.display_name}" in sent_embed.title
    assert any(field.name == "Total XP" and "180" in field.value for field in sent_embed.fields)
    assert any(field.name == "Messages Sent" and "12" in field.value for field in sent_embed.fields)
    assert any(field.name == "Current Role" and "Community Member" in field.value for field in sent_embed.fields)

# Helper for checking if cog_load is called (if it had more complex logic)
@pytest.mark.asyncio
async def test_cog_load_initializes_db(mock_bot):
    """Test that cog_load calls db_manager.init_database."""
    mock_db_m = AsyncMock()
    with patch('src.cogs.gamification_cog.GamificationDBManager', return_value=mock_db_m):
        cog = GamificationCog(bot=mock_bot)
        await cog.cog_load()
        mock_db_m.init_database.assert_called_once()
