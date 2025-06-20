"""
This module defines the GamificationCog class, which handles game mechanics like
XP calculation and level progression for users based on their messages.
"""
import discord
from discord.ext import commands
from discord import app_commands # Ensure app_commands is imported

# Attempt to import from src.gamification, adjust path if necessary for runtime
try:
    from src.gamification.xp_calculator import XPCalculator
    from src.gamification.level_manager import LevelManager
    from src.gamification.contribution_analyzer import ContributionAnalyzer
    from src.gamification.database_manager import GamificationDBManager # Added
except ImportError:
    # Fallback for cases where 'src' is not directly in path, e.g. running from root
    # This might happen in some test/execution environments.
    from gamification.xp_calculator import XPCalculator
    from gamification.level_manager import LevelManager
    from gamification.contribution_analyzer import ContributionAnalyzer
    from gamification.database_manager import GamificationDBManager # Added
from datetime import datetime # Added


class GamificationCog(commands.Cog):
    """
    A Discord Cog for managing gamification features like XP and levels.
    """
    def __init__(self, bot: commands.Bot):
        """
        Initializes the GamificationCog.

        Args:
            bot: The Discord bot instance.
        """
        self.bot = bot
        self.xp_calculator = XPCalculator()
        self.level_manager = LevelManager()
        self.contribution_analyzer = ContributionAnalyzer()

        # Database Manager Setup
        db_path = "wildfire_game.db" # TODO: Move to config
        self.db_manager = GamificationDBManager(db_path)

        # Level-to-role mapping configuration
        # Maps the *starting* level for a role tier.
        self.level_roles_config = {
            1: "Community Member",      # Starts at level 1
            11: "Active Contributor",   # Starts at level 11
            26: "Community Leader",     # Starts at level 26
            51: "Expert/Mentor",        # Starts at level 51
        }
        # Ensure roles are sorted by level for get_role_name_for_level logic
        self._sorted_level_roles = sorted(self.level_roles_config.items(), key=lambda item: item[0], reverse=True)

        print("GamificationCog initialized with level roles config and DB Manager.")

    async def cog_load(self):
        """
        Asynchronous setup that is called when the cog is loaded.
        Ensures the database and necessary tables are initialized.
        """
        await self.db_manager.init_database()
        print("GamificationCog: Database initialized on cog load.")

    # --- Helper Methods ---
    def _create_progress_bar(self, current_value: int, max_value: int, length: int = 10) -> str:
        """
        Creates a simple text-based progress bar.
        Example: [#####-----]
        """
        if max_value == 0: # Avoid division by zero for level 0 or if next level XP is same as current
            return "[----------]" if current_value == 0 else "[##########]"

        filled_length = int(length * current_value // max_value)
        bar = '█' * filled_length + '-' * (length - filled_length)
        return f"[{bar}]"

    async def _generate_level_progress_embed(self, interaction: discord.Interaction, member: discord.Member, is_self_command: bool) -> discord.Embed:
        """
        Generates an embed displaying a user's level, XP, and progress for a given guild.
        """
        if not interaction.guild: # Should be caught by command checks, but defensive
            return discord.Embed(title="Error", description="This command must be used in a server.", color=discord.Color.red())

        guild_id = interaction.guild.id
        user_data = await self.get_db_user_stats_or_default(member.id, guild_id)
        current_xp = user_data['xp']
        current_level = user_data['level']

        title = f"Level Information for {member.display_name}"
        if is_self_command:
            title = f"Your Level & Progress, {member.display_name}"

        embed = discord.Embed(title=title, color=member.color if member.color != discord.Color.default() else discord.Color.blue())
        embed.set_thumbnail(url=member.display_avatar.url)

        if current_level == 0 and current_xp < self.level_manager.get_xp_for_level(1) : # Check against XP for Lvl 1
            embed.description = "You haven't earned any XP yet. Start contributing to the community!"
            if not is_self_command:
                 embed.description = f"{member.display_name} hasn't earned any XP yet."
            embed.add_field(name="Level", value="0")
            embed.add_field(name="Total XP", value=str(current_xp))
            return embed

        xp_for_current_level_start = self.level_manager.get_xp_for_level(current_level)
        xp_for_next_level_start = self.level_manager.get_xp_for_level(current_level + 1)

        xp_needed_for_next_level_range = xp_for_next_level_start - xp_for_current_level_start
        xp_earned_in_current_level = current_xp - xp_for_current_level_start

        embed.add_field(name="Level", value=f"**{current_level}**", inline=True)
        embed.add_field(name="Total XP", value=f"**{current_xp}**", inline=True)

        if is_self_command:
            role_name = self.get_role_name_for_level(current_level)
            embed.add_field(name="Current Role", value=f"{role_name if role_name else 'N/A'}", inline=True)

        if xp_needed_for_next_level_range > 0 :
            progress_bar = self._create_progress_bar(xp_earned_in_current_level, xp_needed_for_next_level_range)
            embed.add_field(
                name=f"Progress to Level {current_level + 1}",
                value=f"{progress_bar} {xp_earned_in_current_level} / {xp_needed_for_next_level_range} XP",
                inline=False
            )
        else: # Max level or XP calculation needs review for this case
             embed.add_field(
                name=f"Progress to Level {current_level + 1}",
                value="Max level reached or XP data requires review.", # Or just show current XP
                inline=False
            )

        # Footer to show who requested it if it's not the user themselves
        if not is_self_command:
            embed.set_footer(text=f"Requested by {interaction.user.display_name}")

        return embed

    def get_role_name_for_level(self, level: int) -> str | None:
        """
        Determines the role name a user qualifies for based on their level.

        Args:
            level: The user's current level.

        Returns:
            The name of the highest tier role the user qualifies for, or None.
        """
        current_role_name = None
        # Iterate through sorted roles (descending level)
        for threshold_level, role_name in self._sorted_level_roles:
            if level >= threshold_level:
                current_role_name = role_name
                break
        return current_role_name

    async def get_db_user_stats_or_default(self, user_id: int, guild_id: int) -> dict:
        """
        Retrieves user stats from the database for a specific guild.
        Returns default values if the user is not found.
        """
        stats = await self.db_manager.get_user_stats(user_id, guild_id)
        if stats:
            return stats
        return {'user_id': user_id, 'guild_id': guild_id, 'xp': 0, 'level': 0, 'message_count': 0, 'last_message_timestamp': ''}

    async def update_db_user_stats(self, user_id: int, guild_id: int, xp: int, level: int, message_count: int):
        """
        Updates user stats in the database for a specific guild.

        Args:
            user_id: The Discord user ID.
            guild_id: The Discord guild ID.
            xp: The new total XP for the user.
            level: The new level for the user.
            message_count: The new message count for the user.
        """
        timestamp = datetime.now().isoformat()
        await self.db_manager.update_user_stats(user_id, guild_id, xp, level, message_count, timestamp)


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Handles message events to grant XP, manage levels, and update roles.
        Now processes only guild messages and uses the database.
        """
        if message.author.bot or not message.guild:
            return # Ignore bot messages and DMs

        user_id = message.author.id
        guild_id = message.guild.id

        # 1. Analyze contribution
        analysis_results = self.contribution_analyzer.analyze_contribution(
            message.content, str(user_id), str(message.channel.id) # channel_id still useful for context
        )

        # 2. Extract flags for XP calculation
        is_helpful = analysis_results.get('is_helpful_answer', False)
        is_solution = analysis_results.get('is_problem_solution', False)
        is_quality_discussion = analysis_results.get('is_quality_discussion', False)
        is_creative = analysis_results.get('is_creative_content', False)
        is_community_assist = analysis_results.get('is_community_assistance', False)
        is_spam = analysis_results.get('is_spam_or_low_quality', False)

        # 3. Calculate base earned XP
        earned_xp = self.xp_calculator.calculate_xp(
            message_content=message.content, # Though not used by current calculate_xp, pass for future
            is_helpful_answer=is_helpful,
            is_problem_solution=is_solution,
            is_quality_discussion=is_quality_discussion,
            is_creative_content=is_creative,
            is_community_assistance=is_community_assist,
            is_spam=is_spam
        )

        # 4. Get current user data from DB
        current_user_data = await self.get_db_user_stats_or_default(user_id, guild_id)
        current_xp = current_user_data['xp']
        current_level = current_user_data['level']
        message_count = current_user_data['message_count'] + 1

        # 5. Apply diminishing returns (using the modified signature)
        earned_xp = self.xp_calculator.apply_diminishing_returns(str(user_id), earned_xp, message_count)

        # 6. Apply channel relevance (placeholder call)
        earned_xp = self.xp_calculator.apply_channel_relevance(str(message.channel.id), earned_xp)

        if earned_xp <= 0 and not is_spam :
            # Still update message count and timestamp even if no XP gained
            await self.update_db_user_stats(user_id, guild_id, current_xp, current_level, message_count)
            # print(f"User {user_id} in guild {guild_id} sent a message. No XP awarded. Total messages: {message_count}")
            return

        # 7. Update total XP and level
        new_total_xp = current_xp + earned_xp
        new_level = self.level_manager.get_level_for_xp(new_total_xp)

        # 8. Update user data in DB
        await self.update_db_user_stats(user_id, guild_id, new_total_xp, new_level, message_count)

        print(f"User {message.author.name} ({user_id}) in guild {guild_id}: +{earned_xp} XP. Total: {new_total_xp}. Level: {new_level}. Messages: {message_count}")

        # 9. Check for level up, send message, and manage roles
        if new_level > current_level:
            level_up_message = f"🎉 Congrats {message.author.mention}, you reached level {new_level}! 🎉"
            try:
                await message.channel.send(level_up_message)
                print(f"Sent level up message to {message.author.name} for reaching level {new_level}")
            except discord.errors.Forbidden:
                print(f"Error: Bot does not have permission to send messages in channel {message.channel.id} for {message.author.name}.")
            except Exception as e:
                print(f"Error sending level up message for {message.author.name}: {e}")

            # Role assignment logic
            if message.guild is None:
                print(f"User {message.author.name} leveled up in DMs. Skipping role assignment.")
            else:
                guild = message.guild
                member = message.author # In guild context, message.author is a Member object

                new_role_name = self.get_role_name_for_level(new_level)
                old_role_name = self.get_role_name_for_level(current_level) # Role they qualified for at their old level

                if new_role_name != old_role_name:
                    print(f"Role change for {member.name}: From '{old_role_name}' to '{new_role_name}'")
                    # Handle removal of old role tier (if it's a managed level role)
                    if old_role_name and old_role_name in self.level_roles_config.values():
                        role_to_remove_obj = discord.utils.get(guild.roles, name=old_role_name)
                        if role_to_remove_obj:
                            if role_to_remove_obj in member.roles:
                                try:
                                    await member.remove_roles(role_to_remove_obj, reason="Level up, new role tier assigned")
                                    print(f"Removed role '{old_role_name}' from {member.name}")
                                except discord.Forbidden:
                                    print(f"Error: Bot lacks permissions to remove role '{old_role_name}' from {member.name} in {guild.name}.")
                                except discord.HTTPException as e_http:
                                    print(f"Error: Failed to remove role '{old_role_name}' from {member.name} due to API error: {e_http}")
                            else:
                                print(f"Info: User {member.name} did not have the old role '{old_role_name}' to remove.")
                        else:
                            print(f"Warning: Old role '{old_role_name}' not found in guild {guild.name} for removal.")

                    # Handle addition of new role tier
                    if new_role_name:
                        target_role_to_add_obj = discord.utils.get(guild.roles, name=new_role_name)
                        if target_role_to_add_obj:
                            if target_role_to_add_obj not in member.roles:
                                try:
                                    await member.add_roles(target_role_to_add_obj, reason="Level up achievement")
                                    print(f"Added role '{new_role_name}' to {member.name}")
                                except discord.Forbidden:
                                    print(f"Error: Bot lacks permissions to add role '{new_role_name}' to {member.name} in {guild.name}.")
                                except discord.HTTPException as e_http:
                                    print(f"Error: Failed to add role '{new_role_name}' to {member.name} due to API error: {e_http}")
                            else:
                                print(f"Info: User {member.name} already has the new role '{new_role_name}'.")
                        else:
                            print(f"Warning: New role '{new_role_name}' not found in guild {guild.name} for assignment.")
                else:
                    print(f"User {member.name} leveled up ({current_level} -> {new_level}), but remains in the same role tier ('{new_role_name}').")

    # --- Slash Commands ---

    @app_commands.command(name="level", description="Check a user's current level and XP.")
    @app_commands.describe(user="The user to check the level for (optional, defaults to yourself).")
    async def level_command(self, interaction: discord.Interaction, user: discord.Member = None):
        """Displays level, XP, and progress for a specified user or the command user."""
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        target_member = user if user else interaction.user
        embed = await self._generate_level_progress_embed(interaction, target_member, is_self_command=(target_member == interaction.user))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="progress", description="Show your personal XP and level progress.")
    async def progress_command(self, interaction: discord.Interaction):
        """Displays your own level, XP, progress, and current role."""
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        embed = await self._generate_level_progress_embed(interaction, interaction.user, is_self_command=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="Show the server XP leaderboard.")
    @app_commands.describe(timeframe="The time period for the leaderboard (currently all-time).")
    async def leaderboard_command(self, interaction: discord.Interaction, timeframe: str = "all_time"):
        """Displays the top users by XP in the server."""
        if not interaction.guild:
            await interaction.response.send_message("Leaderboard is only available in guilds.", ephemeral=True)
            return

        leaderboard_data = await self.db_manager.get_guild_leaderboard(interaction.guild.id, limit=10)

        if not leaderboard_data:
            embed = discord.Embed(title=f"🏆 XP Leaderboard ({interaction.guild.name} - All Time)",
                                  description="The leaderboard is currently empty or no XP has been earned yet.",
                                  color=discord.Color.blue())
            await interaction.response.send_message(embed=embed)
            return

        embed = discord.Embed(title=f"🏆 XP Leaderboard ({interaction.guild.name} - All Time)", color=discord.Color.gold())

        description_lines = []
        rank_emojis = ["🥇", "🥈", "🥉"] # For top 3

        for i, data in enumerate(leaderboard_data): # Top 10 users from DB
            member = interaction.guild.get_member(data['user_id'])
            username = member.display_name if member else f"User ID: {data['user_id']} (Left Guild?)"

            rank_display = rank_emojis[i] if i < len(rank_emojis) else f"**#{i + 1}**"
            description_lines.append(
                f"{rank_display} {username} - Level {data['level']} ({data['xp']} XP)"
            )

        if not description_lines: # Should be caught by `if not leaderboard_data` earlier
            embed.description = "It seems no one has gained XP yet!"
        else:
            embed.description = "\n".join(description_lines)

        embed.set_footer(text=f"Leaderboard timeframe: {timeframe.replace('_', ' ').title()}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="contributions", description="Show a summary of your or another user's contributions.")
    @app_commands.describe(user="The user to check contributions for (optional, defaults to yourself).")
    async def contributions_command(self, interaction: discord.Interaction, user: discord.Member = None):
        """Displays a summary of a user's contributions including XP, level, and message count."""
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        target_member = user if user else interaction.user
        guild_id = interaction.guild.id
        user_data = await self.get_db_user_stats_or_default(target_member.id, guild_id)

        embed = discord.Embed(
            title=f"Contribution Summary for {target_member.display_name}",
            color=target_member.color if target_member.color != discord.Color.default() else discord.Color.green()
        )
        embed.set_thumbnail(url=target_member.display_avatar.url)

        embed.add_field(name="Total XP", value=f"✨ {user_data['xp']}", inline=True)
        embed.add_field(name="Current Level", value=f"🏅 {user_data['level']}", inline=True)
        embed.add_field(name="Messages Sent", value=f"💬 {user_data['message_count']}", inline=True)

        current_role_name = self.get_role_name_for_level(user_data['level'])
        embed.add_field(name="Current Role", value=f"{current_role_name if current_role_name else 'N/A'}", inline=False)

        embed.add_field(name="Detailed History", value="Individual contribution history is not yet available.", inline=False)

        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    """
    Setup function to add the GamificationCog to the bot.
    This is the standard way discord.py loads cogs.
    """
    await bot.add_cog(GamificationCog(bot))
    print("GamificationCog added to bot.")

# Note: The task asked to modify src/discord_wildfire.py to load the cog.
# The setup function above is the standard way to make a cog loadable via bot.load_extension('src.cogs.gamification_cog').
# If direct add_cog is used in discord_wildfire.py, this setup function here isn't strictly necessary for that flow,
# but it's good practice to include it for cog discoverability and alternative loading methods.
# The primary cog loading will be handled in discord_wildfire.py as per task instructions.
