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
    @details Simple slash commands for immediate deployment
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.game = WildfireGame()
        
    @discord.app_commands.command(name="fire", description="Report a new wildfire incident")
    async def fire_command(self, interaction: discord.Interaction):
        """Create new wildfire incident for the channel."""
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
        """Assign player to active fire in channel."""
        # Find active fire in channel (simplified for prototype)
        active_fire = None
        for fire_id, fire_data in self.game.active_fires.items():
            if fire_data["status"] == "active":
                active_fire = fire_data
                break
                
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
                "❌ Unable to assign to incident",
                ephemeral=True
            )
            
    @discord.app_commands.command(name="firestatus", description="Check status of active fires")
    async def status_command(self, interaction: discord.Interaction):
        """Display current fire status."""
        if not self.game.active_fires:
            await interaction.response.send_message(
                "📍 No active fires currently",
                ephemeral=True
            )
            return
            
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
                
        await interaction.response.send_message(embed=embed)


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