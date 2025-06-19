"""
@file discord_wildfire.py
@brief Simple wildfire game commands for Discord integration
@details Following KISS principles - minimal viable wildfire game for immediate deployment
"""

import discord
from discord.ext import commands
import random
import time
from datetime import datetime, timedelta
import json
import os


class SingleplayerGame:
    """
    @brief Personal wildfire game state for DM contexts
    @details User-isolated game state that doesn't interfere with multiplayer
    """
    
    def __init__(self):
        self.user_states = {}
        
    def get_user_state(self, user_id):
        """Get or create personal game state for user."""
        if user_id not in self.user_states:
            self.user_states[user_id] = {
                "active_fires": {},
                "player_assignment": None
            }
        return self.user_states[user_id]
        
    def clear_user_state(self, user_id):
        """Clear all personal game state for user."""
        if user_id in self.user_states:
            del self.user_states[user_id]
            
    def create_personal_fire(self, user_id):
        """Create new fire incident for personal use."""
        user_state = self.get_user_state(user_id)
        fire_id = f"personal_{user_id}_{int(time.time())}"
        
        fire_types = ["grass", "forest", "interface"]
        fire_type = random.choice(fire_types)
        
        fire_data = {
            "id": fire_id,
            "type": fire_type,
            "size_acres": random.randint(5, 50),
            "containment": 0,
            "threat_level": random.choice(["low", "moderate", "high"]),
            "responder_assigned": False,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        user_state["active_fires"][fire_id] = fire_data
        return fire_data
        
    def assign_personal_responder(self, user_id, fire_id):
        """Assign user to their personal fire."""
        user_state = self.get_user_state(user_id)
        
        if fire_id not in user_state["active_fires"]:
            return False
            
        user_state["active_fires"][fire_id]["responder_assigned"] = True
        user_state["player_assignment"] = fire_id
        return True
        
    def get_personal_fire_status(self, user_id, fire_id):
        """Get personal fire status and update progress."""
        user_state = self.get_user_state(user_id)
        
        if fire_id not in user_state["active_fires"]:
            return None
            
        fire = user_state["active_fires"][fire_id]
        
        if fire["responder_assigned"]:
            containment_gain = min(25, 100 - fire["containment"])
            fire["containment"] = min(fire["containment"] + containment_gain, 100)
            
        return fire


class WildfireGame:
    """
    @brief Simple wildfire incident management for Discord
    @details Minimal implementation following coding standards:
    - Functions under 60 lines
    - Single responsibility
    - Descriptive naming
    - Simple state management
    """
    
    def __init__(self):
        self.active_fires = {}
        self.player_assignments = {}
        
    def create_fire(self, channel_id):
        """Create new fire incident with basic properties."""
        fire_id = f"fire_{int(time.time())}"
        
        # Simple fire properties for immediate prototype
        fire_types = ["grass", "forest", "interface"]
        fire_type = random.choice(fire_types)
        
        fire_data = {
            "id": fire_id,
            "type": fire_type,
            "size_acres": random.randint(5, 50),
            "containment": 0,
            "threat_level": random.choice(["low", "moderate", "high"]),
            "responders": [],
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.active_fires[fire_id] = fire_data
        return fire_data
        
    def assign_player(self, fire_id, player_id, player_name):
        """Assign player to fire incident."""
        if fire_id not in self.active_fires:
            return False
            
        if player_id not in self.active_fires[fire_id]["responders"]:
            self.active_fires[fire_id]["responders"].append({
                "id": player_id,
                "name": player_name,
                "role": "firefighter",
                "assigned_at": datetime.now().isoformat()
            })
            
        self.player_assignments[player_id] = fire_id
        return True
        
    def get_fire_status(self, fire_id):
        """Get current fire status for reporting."""
        if fire_id not in self.active_fires:
            return None
            
        fire = self.active_fires[fire_id]
        responder_count = len(fire["responders"])
        
        # Simple progress simulation
        if responder_count > 0:
            containment_gain = min(responder_count * 15, 100 - fire["containment"])
            fire["containment"] = min(fire["containment"] + containment_gain, 100)
            
        return fire


class WildfireCommands(commands.Cog):
    """
    @brief Discord commands for wildfire game
    @details Context-aware commands supporting both DM and Guild modes
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.game = WildfireGame()
        self.singleplayer_game = SingleplayerGame()
        
    @discord.app_commands.command(name="fire", description="Report a new wildfire incident")
    async def fire_command(self, interaction: discord.Interaction):
        """Create new wildfire incident - context-aware for DM vs Guild."""
        if interaction.guild is None:
            await self._handle_singleplayer_fire(interaction)
        else:
            await self._handle_multiplayer_fire(interaction)
            
    async def _handle_singleplayer_fire(self, interaction: discord.Interaction):
        """Handle fire creation in DM (singleplayer mode)."""
        fire_data = self.singleplayer_game.create_personal_fire(interaction.user.id)
        
        embed = discord.Embed(
            title="🔥 PERSONAL WILDFIRE INCIDENT",
            description=f"You've encountered a {fire_data['type']} fire",
            color=0xFF4500
        )
        
        embed.add_field(
            name="📍 Incident Details",
            value=f"**Fire ID:** {fire_data['id'].split('_')[-1]}\n"
                  f"**Size:** {fire_data['size_acres']} acres\n"
                  f"**Threat Level:** {fire_data['threat_level'].upper()}\n"
                  f"**Containment:** {fire_data['containment']}%",
            inline=False
        )
        
        embed.add_field(
            name="🚒 Solo Response",
            value="Use `/respond` to start your firefighting response",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
        
    async def _handle_multiplayer_fire(self, interaction: discord.Interaction):
        """Handle fire creation in Guild (multiplayer mode)."""
        fire_data = self.game.create_fire(interaction.channel.id)
        
        embed = discord.Embed(
            title="🔥 WILDFIRE INCIDENT REPORTED",
            description=f"New {fire_data['type']} fire detected",
            color=0xFF4500
        )
        
        embed.add_field(
            name="📍 Incident Details",
            value=f"**Fire ID:** {fire_data['id']}\n"
                  f"**Size:** {fire_data['size_acres']} acres\n"
                  f"**Threat Level:** {fire_data['threat_level'].upper()}\n"
                  f"**Containment:** {fire_data['containment']}%",
            inline=False
        )
        
        embed.add_field(
            name="🚒 Response Needed",
            value="Use `/respond` to join the incident response team",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
        
    @discord.app_commands.command(name="respond", description="Respond to active wildfire incident")
    async def respond_command(self, interaction: discord.Interaction):
        """Assign player to active fire - context-aware for DM vs Guild."""
        if interaction.guild is None:
            await self._handle_singleplayer_respond(interaction)
        else:
            await self._handle_multiplayer_respond(interaction)
            
    async def _handle_singleplayer_respond(self, interaction: discord.Interaction):
        """Handle response assignment in DM (singleplayer mode)."""
        user_state = self.singleplayer_game.get_user_state(interaction.user.id)
        active_fire = self._find_active_personal_fire(user_state)
        
        if not active_fire:
            await interaction.response.send_message(
                "❌ No active personal fires. Use `/fire` to create an incident.",
                ephemeral=True
            )
            return
            
        success = self.singleplayer_game.assign_personal_responder(
            interaction.user.id, active_fire["id"]
        )
        
        if success:
            await interaction.response.send_message(
                f"✅ You are now responding to fire {active_fire['id'].split('_')[-1]}"
            )
        else:
            await interaction.response.send_message(
                "❌ Unable to assign to incident", ephemeral=True
            )
            
    async def _handle_multiplayer_respond(self, interaction: discord.Interaction):
        """Handle response assignment in Guild (multiplayer mode)."""
        active_fire = self._find_active_guild_fire()
        
        if not active_fire:
            await interaction.response.send_message(
                "❌ No active fires to respond to. Use `/fire` to create an incident.",
                ephemeral=True
            )
            return
            
        success = self.game.assign_player(
            active_fire["id"],
            interaction.user.id, 
            interaction.user.display_name
        )
        
        if success:
            await interaction.response.send_message(
                f"✅ {interaction.user.display_name} assigned to {active_fire['id']} as firefighter"
            )
        else:
            await interaction.response.send_message(
                "❌ Unable to assign to incident", ephemeral=True
            )
            
    def _find_active_personal_fire(self, user_state):
        """Find first active personal fire for user."""
        for fire_data in user_state["active_fires"].values():
            if fire_data["status"] == "active":
                return fire_data
        return None
        
    def _find_active_guild_fire(self):
        """Find first active guild fire."""
        for fire_data in self.game.active_fires.values():
            if fire_data["status"] == "active":
                return fire_data
        return None
            
    @discord.app_commands.command(name="firestatus", description="Check status of active fires")
    async def status_command(self, interaction: discord.Interaction):
        """Display current fire status - context-aware for DM vs Guild."""
        if interaction.guild is None:
            await self._handle_singleplayer_status(interaction)
        else:
            await self._handle_multiplayer_status(interaction)
            
    async def _handle_singleplayer_status(self, interaction: discord.Interaction):
        """Handle status display in DM (singleplayer mode)."""
        user_state = self.singleplayer_game.get_user_state(interaction.user.id)
        
        if not user_state["active_fires"]:
            await interaction.response.send_message(
                "📍 No personal fires currently", ephemeral=True
            )
            return
            
        embed = self._create_personal_status_embed(interaction.user.id, user_state)
        await interaction.response.send_message(embed=embed)
        
    async def _handle_multiplayer_status(self, interaction: discord.Interaction):
        """Handle status display in Guild (multiplayer mode)."""
        if not self.game.active_fires:
            await interaction.response.send_message(
                "📍 No active fires currently", ephemeral=True
            )
            return
            
        embed = self._create_guild_status_embed()
        await interaction.response.send_message(embed=embed)
        
    def _create_personal_status_embed(self, user_id, user_state):
        """Create status embed for personal fires."""
        embed = discord.Embed(
            title="🔥 YOUR ACTIVE INCIDENTS",
            color=0xFF6B35
        )
        
        for fire_id, fire_data in user_state["active_fires"].items():
            if fire_data["status"] == "active":
                current_status = self.singleplayer_game.get_personal_fire_status(user_id, fire_id)
                
                status_text = (
                    f"**Size:** {current_status['size_acres']} acres\n"
                    f"**Containment:** {current_status['containment']}%\n"
                    f"**Response:** {'Assigned' if current_status['responder_assigned'] else 'Needed'}"
                )
                
                display_id = fire_id.split('_')[-1]
                embed.add_field(
                    name=f"🚨 FIRE {display_id.upper()}",
                    value=status_text,
                    inline=True
                )
                
        return embed
        
    def _create_guild_status_embed(self):
        """Create status embed for guild fires."""
        embed = discord.Embed(
            title="🔥 ACTIVE INCIDENTS STATUS",
            color=0xFF6B35
        )
        
        for fire_id, fire_data in self.game.active_fires.items():
            if fire_data["status"] == "active":
                current_status = self.game.get_fire_status(fire_id)
                responder_names = [r["name"] for r in current_status["responders"]]
                
                status_text = (
                    f"**Size:** {current_status['size_acres']} acres\n"
                    f"**Containment:** {current_status['containment']}%\n"
                    f"**Responders:** {len(responder_names)}\n"
                    f"**Team:** {', '.join(responder_names) if responder_names else 'None'}"
                )
                
                embed.add_field(
                    name=f"🚨 {fire_id.upper()}",
                    value=status_text,
                    inline=True
                )
                
        return embed
        
    @discord.app_commands.command(name="clear", description="🧹 Reset personal game state (DM only)")
    async def clear_command(self, interaction: discord.Interaction):
        """Clear all personal game state for development/testing."""
        if interaction.guild is not None:
            await interaction.response.send_message(
                "❌ Debug commands only work in DM", ephemeral=True
            )
            return
            
        self.singleplayer_game.clear_user_state(interaction.user.id)
        await interaction.response.send_message("✅ Personal game state cleared")
        
    @discord.app_commands.command(name="start", description="🚀 Begin new singleplayer scenario (DM only)")
    async def start_command(self, interaction: discord.Interaction):
        """Start fresh singleplayer scenario for development/testing."""
        if interaction.guild is not None:
            await interaction.response.send_message(
                "❌ Debug commands only work in DM", ephemeral=True
            )
            return
            
        self.singleplayer_game.clear_user_state(interaction.user.id)
        await interaction.response.send_message(
            "🎮 **New Singleplayer Session Started**\n"
            "Ready for wildfire incident command training.\n"
            "Use `/fire` to create your first incident."
        )
        
    @discord.app_commands.command(name="stop", description="🛑 End current session (DM only)")
    async def stop_command(self, interaction: discord.Interaction):
        """End current singleplayer session cleanly."""
        if interaction.guild is not None:
            await interaction.response.send_message(
                "❌ Debug commands only work in DM", ephemeral=True
            )
            return
            
        user_state = self.singleplayer_game.get_user_state(interaction.user.id)
        active_count = len([f for f in user_state["active_fires"].values() 
                           if f["status"] == "active"])
        
        self.singleplayer_game.clear_user_state(interaction.user.id)
        
        await interaction.response.send_message(
            f"🏁 **Session Ended**\n"
            f"Closed {active_count} active incident(s).\n"
            f"Use `/start` to begin a new session."
        )


async def setup_wildfire_commands(bot):
    """
    @brief Add wildfire commands to existing bot
    @details Simple integration function for BlazeBot
    """
    await bot.add_cog(WildfireCommands(bot))
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"🔥 Synced {len(synced)} wildfire commands")
    except Exception as e:
        print(f"Failed to sync wildfire commands: {e}")