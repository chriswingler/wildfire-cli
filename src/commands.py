"""
Wildfire Discord Game Command Handler
=====================================

This module provides the core command handling for the Wildfire Discord game,
a simplified MMORPG focused on wildfire response scenarios. It includes game logic
management, database interaction for persisting game state, and Discord bot command
registration using `discord.py`.

The primary components are:
  - ``WildfireGame``: Manages game state, fire creation, responder assignment, and database operations.
  - ``WildfireCommands``: A Discord Cog that groups related commands and event listeners.
  - ``setup``: Function to initialize and add the Cog and application commands to the bot.
"""

import discord
from discord.ext import commands
import os
import logging
import asyncio
import traceback
from datetime import datetime, timedelta
import time
import random
import aiosqlite
from utilities import CooldownManager
from ui.hud_components import HUDComponents, HUDColors, HUDEmojis


class WildfireGame:
    """
    Manages the core game logic and database interactions for wildfire incidents.

    This class is responsible for creating and tracking fires, assigning responders,
    and persisting game state to an SQLite database. It handles the underlying
    mechanics of the wildfire simulation.
    """
    
    def __init__(self, db_path: str = "wildfire_game.db"):
        """
        Initializes the WildfireGame instance.

        :param db_path: Path to the SQLite database file.
        :type db_path: str
        """
        self.db_path = db_path
        self.active_fires = {}  # In-memory cache, though primary state is in DB
        
    async def init_database(self):
        """
        Initializes the SQLite database and creates necessary tables if they don't exist.

        This method sets up the `fires` and `responders` tables required for game operation.
        It should be called once when the game system starts.
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS fires (
                    id TEXT PRIMARY KEY,
                    server_id INTEGER,
                    channel_id INTEGER,
                    fire_type TEXT,
                    size_acres INTEGER,
                    containment INTEGER,
                    threat_level TEXT,
                    status TEXT,
                    created_at TEXT
                )
            ''')
            
            await db.execute('''
                CREATE TABLE IF NOT EXISTS responders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fire_id TEXT,
                    user_id INTEGER,
                    user_name TEXT,
                    role TEXT,
                    assigned_at TEXT,
                    FOREIGN KEY (fire_id) REFERENCES fires (id)
                )
            ''')
            
            await db.commit()
            
    async def create_fire(self, server_id: int, channel_id: int) -> dict:
        """
        Creates a new wildfire incident in the specified server and channel.

        The fire details (type, size, threat level) are randomly generated.
        The new fire is stored in the database and basic information is returned.

        :param server_id: The Discord server ID where the fire is created.
        :type server_id: int
        :param channel_id: The Discord channel ID where the fire is created.
        :type channel_id: int
        :return: A dictionary containing the details of the created fire.
        :rtype: dict
        """
        fire_id = f"fire_{int(time.time())}"
        fire_types = ["grass", "forest", "interface"]
        fire_type = random.choice(fire_types)
        
        fire_data = {
            "id": fire_id,
            "server_id": server_id,
            "channel_id": channel_id,
            "type": fire_type,
            "size_acres": random.randint(5, 50),
            "containment": 0,
            "threat_level": random.choice(["low", "moderate", "high"]),
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO fires (id, server_id, channel_id, fire_type, 
                                 size_acres, containment, threat_level, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (fire_id, server_id, channel_id, fire_type, 
                  fire_data["size_acres"], 0, fire_data["threat_level"], 
                  "active", fire_data["created_at"]))
            await db.commit()
            
        return fire_data
        
    async def assign_responder(self, fire_id: str, user_id: int, user_name: str) -> bool:
        """
        Assigns a player (responder) to an active fire incident.

        Stores the responder's information in the database, linking them to the specified fire.
        If the responder is already assigned, this operation might be ignored by the DB
        due to 'INSERT OR IGNORE'.

        :param fire_id: The ID of the fire to assign the responder to.
        :type fire_id: str
        :param user_id: The Discord user ID of the responder.
        :type user_id: int
        :param user_name: The display name of the responder.
        :type user_name: str
        :return: True if the assignment was attempted (database will handle uniqueness).
        :rtype: bool
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR IGNORE INTO responders (fire_id, user_id, user_name, role, assigned_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (fire_id, user_id, user_name, "firefighter", datetime.now().isoformat()))
            await db.commit()
            return True
            
    async def get_active_fires(self, server_id: int) -> list[dict]:
        """
        Retrieves a list of all active fires for a given server.

        This method queries the database for fires with 'active' status.
        It also calculates the current containment level based on the number of responders
        and updates the fire's status to 'contained' if 100% containment is reached.

        :param server_id: The Discord server ID for which to retrieve active fires.
        :type server_id: int
        :return: A list of dictionaries, where each dictionary represents an active fire
                 and includes its details and responder count.
        :rtype: list[dict]
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT * FROM fires WHERE server_id = ? AND status = 'active'
            ''', (server_id,)) as cursor:
                fires = await cursor.fetchall()
                
            fire_list = []
            for fire in fires:
                async with db.execute('''
                    SELECT COUNT(*) FROM responders WHERE fire_id = ?
                ''', (fire[0],)) as cursor:
                    responder_count = (await cursor.fetchone())[0]
                    
                # Simplified containment progression logic for database-tracked fires.
                # This is distinct from the more complex simulation in fire_engine.py.
                # Each responder contributes a fixed amount (e.g., 10%) to containment.
                # The fire's original containment value is fire[5].
                current_db_containment = fire[5]
                containment = min(current_db_containment + (responder_count * 10), 100)
                
                # If containment reaches 100%, update the fire's status in the database.
                if containment >= 100:
                    await db.execute('''
                        UPDATE fires SET status = 'contained' WHERE id = ?
                    ''', (fire[0],))
                    await db.commit()
                    
                fire_list.append({
                    "id": fire[0],
                    "type": fire[3],
                    "size_acres": fire[4],
                    "containment": containment,
                    "threat_level": fire[6],
                    "responder_count": responder_count
                })
                
            return fire_list


class WildfireCommands(commands.Cog):
    """
    A Discord Cog for handling wildfire MMORPG commands and related events.

    This class groups game-specific commands, event listeners (like `on_ready`),
    and utility functions. It uses an instance of `WildfireGame` to interact
    with the game logic and database.
    """
    
    def __init__(self, bot: commands.Bot):
        """
        Initializes the WildfireCommands Cog.

        :param bot: The Discord bot instance.
        :type bot: commands.Bot
        """
        self.bot = bot
        self.game = WildfireGame()
        self.cooldown = CooldownManager()
        
    async def cog_load(self):
        """
        Asynchronous setup that runs when the Cog is loaded.

        This method ensures the game database is initialized.
        """
        await self.game.init_database()
        
    async def add_safe_reaction(self, message: discord.Message, emoji: str):
        """
        Safely adds a reaction to a message, handling potential rate limits.

        If a rate limit (HTTP 429) is encountered, it will wait for the specified
        `Retry-After` duration and attempt to add the reaction again.

        :param message: The Discord message object to react to.
        :type message: discord.Message
        :param emoji: The emoji to use for the reaction.
        :type emoji: str
        """
        try:
            if self.cooldown.check_reaction(message):
                await message.add_reaction(emoji)
                self.cooldown.update_reaction(message)
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = float(e.response.headers.get('Retry-After', 1.5))
                await asyncio.sleep(retry_after)
                await self.add_safe_reaction(message, emoji)
            else:
                logging.error(f"Reaction failed: {str(e)}")

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Event listener triggered when the bot is ready and connected to Discord.

        Sets the bot's presence (status) and syncs application commands
        to all connected guilds. It logs information about the syncing process
        and the number of servers the bot is connected to.
        """
        await self.bot.change_presence(activity=discord.Game(name="🔥 Wildfire Response MMORPG"))
        
        # Debug command tree state
        commands_in_tree = [cmd.name for cmd in self.bot.tree.get_commands()]
        logging.info(f"🔥 Commands in tree: {commands_in_tree}")
        
        # Sync commands to guilds
        try:
            total_synced = 0
            for guild in self.bot.guilds:
                synced = await self.bot.tree.sync(guild=guild)
                total_synced += len(synced)
                logging.info(f"🔥 Synced {len(synced)} commands to guild {guild.name}")
                if synced:
                    logging.info(f"🔥 Commands synced: {[cmd['name'] for cmd in synced]}")
            logging.info(f"🔥 Total {total_synced} wildfire commands synced")
        except Exception as e:
            logging.error(f"Failed to sync commands: {e}")
            
        logging.info(f"🔥 Wildfire bot online in {len(self.bot.guilds)} servers")

    # Commands moved to setup() function. Docstrings for those are in the setup() function below.
    # The original methods like `fire_command` here are commented out or removed in the actual
    # file, so their docstrings are not needed here. Their functionality is now within
    # the app command definitions in `setup`.

    # @discord.app_commands.command(name="fire", description="🔥 Report a new wildfire incident")
    # async def fire_command(self, interaction: discord.Interaction):
    # """ This is an example of where a command docstring *would* go if it were a Cog method.
    #     However, these commands are now defined in `setup`.
    # """
    #    fire_data = await self.game.create_fire(interaction.guild.id, interaction.channel.id)
    #    embed = discord.Embed(
    # ...
        
    @discord.app_commands.command(name="respond", description="🚒 Respond to active wildfire incident")
    async def respond_command(self, interaction: discord.Interaction):
        """
        Allows a user to respond to an active wildfire incident.

        This is a placeholder as the actual command is defined in `setup`.
        If this Cog method were active, it would assign the interacting user
        as a responder to an ongoing fire.

        :param interaction: The Discord interaction object.
        :type interaction: discord.Interaction
        """
        # Actual implementation is in setup()
        await interaction.response.send_message("This command is handled by the dynamic setup.", ephemeral=True)

    @discord.app_commands.command(name="firestatus", description="📊 Check status of active fires")
    async def status_command(self, interaction: discord.Interaction):
        """
        Displays the status of current active wildfire incidents.

        This is a placeholder as the actual command is defined in `setup`.
        If this Cog method were active, it would fetch and show data about
        ongoing fires.

        :param interaction: The Discord interaction object.
        :type interaction: discord.Interaction
        """
        # Actual implementation is in setup()
        await interaction.response.send_message("This command is handled by the dynamic setup.", ephemeral=True)


async def setup(bot: commands.Bot):
    """
    Sets up the Wildfire Bot by initializing and adding the `WildfireCommands` Cog
    and defining application (slash) commands directly on the bot's command tree.

    This approach is used for reliable command synchronization with Discord.
    The commands defined here utilize the methods from an instance of `WildfireCommands` (Cog)
    to interact with the game logic.

    :param bot: The Discord bot instance.
    :type bot: commands.Bot
    """
    # Add cog for event handlers and utilities
    cog = WildfireCommands(bot)
            title="🔥 WILDFIRE INCIDENT REPORTED",
            description=f"New **{fire_data['type']} fire** detected requiring immediate response",
            color=0xFF4500
        )
        
        embed.add_field(
            name="📍 Incident Details",
            value=f"**Fire ID:** `{fire_data['id']}`\n"
                  f"**Type:** {fire_data['type'].title()} Fire\n"
                  f"**Size:** {fire_data['size_acres']} acres\n"
                  f"**Threat Level:** {fire_data['threat_level'].upper()}\n"
                  f"**Containment:** {fire_data['containment']}%",
            inline=False
        )
        
    await bot.add_cog(cog)
    
    # Define commands directly on bot tree for reliable sync
    @bot.tree.command(name="fire", description="🔥 Report a new wildfire incident")
    async def fire_command(interaction: discord.Interaction):
        """
        Reports a new wildfire incident in the current channel. (App Command)

        This slash command initializes a new fire event using `WildfireGame.create_fire()`,
        stores it, and sends an embed message to the channel with incident details.

        :param interaction: The Discord interaction object from the slash command.
        :type interaction: discord.Interaction
        """
        fire_data = await cog.game.create_fire(interaction.guild.id, interaction.channel.id)
        
        # Convert fire_data to fire_status format for minimal embed
        fire_status = {
            'incident_name': fire_data.get('id', 'Unknown Fire'),
            'fire_size_acres': fire_data.get('size_acres', 0),
            'containment_percent': fire_data.get('containment', 0),
            'threat_level': fire_data.get('threat_level', 'MODERATE'),
            'threatened_structures': fire_data.get('threatened_structures', 0),
            'resources_deployed': fire_data.get('resources_deployed', {'hand_crews': 0, 'engines': 0, 'air_tankers': 0, 'dozers': 0}),
            'team_budget': fire_data.get('team_budget', 50000),
            'operational_period': 1,
            'game_phase': 'active'
        }
        
        # Get fire grid if available
        fire_grid = fire_data.get('fire_grid', None)
        
        # Use minimal incident embed
        embed = HUDComponents.create_incident_embed(
            fire_data.get('id', 'Unknown Fire'),
            fire_status,
            fire_grid
        )
        
        # Add team response info
        embed.add_field(
            name="👥 TEAM RESPONSE",
            value="`Use /respond to join the firefighting team!`",
            inline=False
        )
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="respond", description="🚒 Respond to active wildfire incident")
    async def respond_command(interaction: discord.Interaction):
        """
        Allows a user to respond to an active wildfire incident. (App Command)

        This slash command assigns the interacting user as a responder to the
        earliest active fire in the server. It uses `WildfireGame.assign_responder()`
        and `WildfireGame.get_active_fires()`. An embed message confirms
        the assignment or informs if no active fires are available.

        :param interaction: The Discord interaction object from the slash command.
        :type interaction: discord.Interaction
        """
        active_fires = await cog.game.get_active_fires(interaction.guild.id)
        
        if not active_fires:
            embed = HUDComponents.create_error_embed(
                "NO ACTIVE FIRES",
                "No active fires requiring response.",
                ["Use `/fire` to create an incident."]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        # Assign to first active fire
        fire = active_fires[0]
        success = await cog.game.assign_responder(
            fire["id"],
            interaction.user.id,
            interaction.user.display_name
        )
        
        if success:
            embed = HUDComponents.create_action_embed(
                "RESPONDER ASSIGNED",
                f"{interaction.user.display_name} deployed to **{fire['id']}**",
                True
            )
            
            embed.add_field(
                name=f"{HUDEmojis.CREW} ║ ASSIGNMENT DETAILS",
                value=f"```\n"
                      f"Role:       Firefighter\n"
                      f"Fire Type:  {fire['type'].title()}\n"
                      f"Team Size:  {fire['responder_count'] + 1:>6}\n"
                      f"```",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
        else:
            embed = HUDComponents.create_error_embed(
                "ASSIGNMENT FAILED",
                "Unable to assign to incident - please try again."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @bot.tree.command(name="firestatus", description="📊 Check status of active fires")
    async def firestatus_command(interaction: discord.Interaction):
        """
        Displays the status of current active wildfire incidents. (App Command)

        This slash command retrieves active fires using `WildfireGame.get_active_fires()`
        and presents them in an embed message. If no fires are active, it informs the user.

        :param interaction: The Discord interaction object from the slash command.
        :type interaction: discord.Interaction
        """
        active_fires = await cog.game.get_active_fires(interaction.guild.id)
        
        if not active_fires:
            embed = HUDComponents.create_simple_info_embed(
                "NO ACTIVE FIRES",
                "All incidents contained or controlled.",
                [{"name": f"{HUDEmojis.SUCCESS} ║ OPERATIONAL STATUS", 
                  "value": "No wildfire incidents currently requiring response.", 
                  "inline": False}]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        embed = HUDComponents.create_minimal_embed(
            f"🔥 ACTIVE INCIDENTS ({len(active_fires)})",
            "warning"
        )
        
        # Show up to 3 fires in compact format
        for i, fire in enumerate(active_fires[:3]):
            # Determine status
            containment = fire["containment"]
            if containment > 75:
                status = "🟢 CONTROLLED"
            elif containment > 25:
                status = "🟡 ACTIVE"
            else:
                status = "🔴 CRITICAL"
            
            # Progress bar for containment
            progress_bar = HUDComponents.create_progress_bar(containment, 15)
            
            embed.add_field(
                name=f"{fire['id'].upper()}",
                value=f"`{fire['size_acres']} acres • {fire['responder_count']} team`\n"
                      f"`{progress_bar}`\n"
                      f"{status}",
                inline=True
            )
            
        # Add action if more fires exist
        if len(active_fires) > 3:
            embed.add_field(
                name="➕ MORE FIRES",
                value=f"`+{len(active_fires) - 3} additional incidents`",
                inline=True
            )
        await interaction.response.send_message(embed=embed)
    
    logging.info("🔥 Wildfire commands cog loaded")