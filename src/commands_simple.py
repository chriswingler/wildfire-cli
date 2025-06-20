"""
@file commands_simple.py
@brief Simplified wildfire Discord game commands
@details Direct bot tree commands for reliable sync
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


class WildfireGame:
    """
    @brief Core wildfire game logic with database persistence
    @details Simple implementation following coding standards
    """
    
    def __init__(self, db_path="wildfire_game.db"):
        self.db_path = db_path
        self.active_fires = {}
        
    async def init_database(self):
        """Initialize SQLite database for game state."""
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
            
    async def create_fire(self, server_id, channel_id):
        """Create new fire incident."""
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
        
    async def assign_responder(self, fire_id, user_id, user_name):
        """Assign player to fire incident."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR IGNORE INTO responders (fire_id, user_id, user_name, role, assigned_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (fire_id, user_id, user_name, "firefighter", datetime.now().isoformat()))
            await db.commit()
            return True
            
    async def get_active_fires(self, server_id):
        """Get active fires for a server."""
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
                    
                # Simple containment progression
                containment = min(fire[5] + (responder_count * 10), 100)
                
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
    @brief Discord event handlers for wildfire MMORPG
    @details Simplified command structure focused on game functionality
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.game = WildfireGame()
        self.cooldown = CooldownManager()
        
    async def cog_load(self):
        """Initialize game database when cog loads."""
        await self.game.init_database()

    @commands.Cog.listener()
    async def on_ready(self):
        """Bot startup handler."""
        await self.bot.change_presence(activity=discord.Game(name="🔥 Wildfire Response MMORPG"))
        
        # Debug command tree state
        commands_in_tree = [cmd.name for cmd in self.bot.tree.get_commands()]
        logging.info(f"🔥 Commands in tree: {commands_in_tree}")
        
        # Copy global commands to each guild then sync
        try:
            total_synced = 0
            for guild in self.bot.guilds:
                # Copy global commands to this guild
                self.bot.tree.copy_global_to(guild=guild)
                
                # Now sync guild-specific commands (includes copied globals)
                synced = await self.bot.tree.sync(guild=guild)
                total_synced += len(synced)
                logging.info(f"🔥 Synced {len(synced)} commands to guild {guild.name}")
                if synced:
                    logging.info(f"🔥 Commands synced: {[cmd['name'] for cmd in synced]}")
            logging.info(f"🔥 Total {total_synced} wildfire commands synced")
        except Exception as e:
            logging.error(f"Failed to sync commands: {e}")
            
        logging.info(f"🔥 Wildfire bot online in {len(self.bot.guilds)} servers")


async def setup(bot):
    """
    @brief Setup function for wildfire bot
    @details Initialize and add wildfire commands directly to bot tree
    """
    # Add cog for event handlers and game logic
    cog = WildfireCommands(bot)
    await bot.add_cog(cog)
    
    # Define commands directly on bot tree for reliable sync
    @bot.tree.command(name="fire", description="🔥 Report a new wildfire incident")
    async def fire_command(interaction: discord.Interaction):
        """Create new wildfire incident."""
        fire_data = await cog.game.create_fire(interaction.guild.id, interaction.channel.id)
        
        embed = discord.Embed(
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
        
        embed.add_field(
            name="🚒 Response Commands",
            value="• `/respond` - Join the firefighting response team\n"
                  "• `/firestatus` - Check status of all active incidents",
            inline=False
        )
        
        embed.set_footer(text="Incident Command System • Educational Wildfire Simulation")
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="respond", description="🚒 Respond to active wildfire incident")
    async def respond_command(interaction: discord.Interaction):
        """Assign player to active fire."""
        active_fires = await cog.game.get_active_fires(interaction.guild.id)
        
        if not active_fires:
            await interaction.response.send_message(
                "❌ No active fires requiring response. Use `/fire` to create an incident.",
                ephemeral=True
            )
            return
            
        # Assign to first active fire
        fire = active_fires[0]
        success = await cog.game.assign_responder(
            fire["id"],
            interaction.user.id,
            interaction.user.display_name
        )
        
        if success:
            embed = discord.Embed(
                title="✅ RESPONDER ASSIGNED",
                description=f"{interaction.user.display_name} deployed to **{fire['id']}**",
                color=0x00AA00
            )
            embed.add_field(
                name="Assignment Details",
                value=f"**Role:** Firefighter\n"
                      f"**Fire Type:** {fire['type'].title()}\n"
                      f"**Current Team Size:** {fire['responder_count'] + 1}",
                inline=False
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                "❌ Unable to assign to incident. Try again.",
                ephemeral=True
            )
    
    @bot.tree.command(name="firestatus", description="📊 Check status of active fires")
    async def firestatus_command(interaction: discord.Interaction):
        """Display current fire status."""
        active_fires = await cog.game.get_active_fires(interaction.guild.id)
        
        if not active_fires:
            await interaction.response.send_message(
                "📍 No active fires currently. All incidents contained or controlled.",
                ephemeral=True
            )
            return
            
        embed = discord.Embed(
            title="🔥 ACTIVE INCIDENTS STATUS BOARD",
            description="Current wildfire incidents requiring response",
            color=0xFF6B35
        )
        
        for fire in active_fires[:6]:
            status_color = "🟢" if fire["containment"] > 75 else "🟡" if fire["containment"] > 25 else "🔴"
            
            embed.add_field(
                name=f"{status_color} {fire['id'].upper()}",
                value=f"**Type:** {fire['type'].title()}\n"
                      f"**Size:** {fire['size_acres']} acres\n"
                      f"**Containment:** {fire['containment']}%\n"
                      f"**Responders:** {fire['responder_count']}\n"
                      f"**Threat:** {fire['threat_level'].upper()}",
                inline=True
            )
            
        embed.set_footer(text=f"Incident Command System • {len(active_fires)} active incidents")
        await interaction.response.send_message(embed=embed)
    
    logging.info("🔥 Wildfire commands loaded directly to bot tree")