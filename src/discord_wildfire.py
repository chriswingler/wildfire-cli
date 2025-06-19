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
from fire_engine import FireGrid, WeatherConditions
from incident_reports import IncidentReportGenerator
import asyncio


class TacticalChoicesView(discord.ui.View):
    """Interactive button choices for tactical decisions."""
    
    def __init__(self, singleplayer_game, user_id):
        super().__init__(timeout=300)  # 5 minute timeout
        self.singleplayer_game = singleplayer_game
        self.user_id = user_id
    
    @discord.ui.button(label='1️⃣ Ground Crews - Fast Attack (2pts)', style=discord.ButtonStyle.primary, custom_id='deploy_crews')
    async def deploy_crews(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your incident!", ephemeral=True)
            return
            
        result = self.singleplayer_game.deploy_resources(self.user_id, "hand_crews", 1)
        await self._handle_choice_result(interaction, "Ground Crews", result)
    
    @discord.ui.button(label='2️⃣ Air Support - Heavy Power (5pts)', style=discord.ButtonStyle.danger, custom_id='deploy_air')
    async def deploy_air(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your incident!", ephemeral=True)
            return
            
        result = self.singleplayer_game.deploy_resources(self.user_id, "air_tankers", 1)
        await self._handle_choice_result(interaction, "Air Support", result)
    
    @discord.ui.button(label='3️⃣ Engine Company - Balanced (3pts)', style=discord.ButtonStyle.secondary, custom_id='deploy_engines')
    async def deploy_engines(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your incident!", ephemeral=True)
            return
            
        result = self.singleplayer_game.deploy_resources(self.user_id, "engines", 1)
        await self._handle_choice_result(interaction, "Engine Company", result)
    
    async def _handle_choice_result(self, interaction, resource_name, result):
        """Handle the result of a tactical choice."""
        if result["success"]:
            # Show auto-progression if it happened
            auto = result.get("auto_progression")
            auto_message = ""
            if auto:
                if auto["points_earned"] > 0:
                    auto_message = f"\n\n📈 **PERFORMANCE BONUS: +{auto['points_earned']} pts!**\nGreat containment work!"
                else:
                    auto_message = f"\n\n📉 **FIRE SPREADING!**\nNeed more suppression - deploy fast!"
            
            # Get current fire status after deployment
            user_state = self.singleplayer_game.get_user_state(self.user_id)
            stats = user_state["fire_grid"].get_fire_statistics()
            threats = user_state["fire_grid"].get_threat_assessment()
            
            threat_emoji = "🔴" if threats['threat_level'] == "HIGH" else "🟡" if threats['threat_level'] == "MODERATE" else "🟢"
            
            message = f"""🚒 **{resource_name.upper()} DEPLOYED!**


🔥 **CURRENT FIRE STATUS:**
• **Size:** {stats['fire_size_acres']} acres
• **Containment:** {stats['containment_percent']}%
• **Threat:** {threat_emoji} {threats['threat_level']} - {threats['threatened_structures']} structures at risk


💰 **Budget:** {result['remaining_budget']} points remaining
{auto_message}


**Continue fighting the fire:**"""
            
            # Create new tactical choices view
            view = TacticalChoicesView(self.singleplayer_game, self.user_id)
            await interaction.response.send_message(message, view=view)
            
        else:
            message = f"""❌ **INSUFFICIENT BUDGET**

**Need {result['cost']} pts, have {result['budget']} pts**

💡 **EARN MORE POINTS:** Good containment = more budget!
Try **Ground Crews** (2 pts) - most cost-effective option."""
            
            await interaction.response.send_message(message, ephemeral=True)


class SingleplayerGame:
    """
    @brief Personal wildfire game state for DM contexts
    @details User-isolated game state with realistic fire simulation
    """
    
    def __init__(self):
        self.user_states = {}
        self.report_generator = IncidentReportGenerator()
        
    def get_user_state(self, user_id):
        """Get or create personal game state for user."""
        if user_id not in self.user_states:
            self.user_states[user_id] = {
                "fire_grid": None,
                "incident_name": None,
                "resources_deployed": {"hand_crews": 0, "engines": 0, "air_tankers": 0},
                "operational_period": 1,
                "last_update": datetime.now(),
                "game_phase": "ready",  # ready, active, contained, completed
                "budget": 10,  # Starting resource budget
                "score": 0  # Performance score
            }
        return self.user_states[user_id]
        
    def clear_user_state(self, user_id):
        """Clear all personal game state for user."""
        if user_id in self.user_states:
            del self.user_states[user_id]
            
    def start_new_scenario(self, user_id, difficulty="moderate"):
        """Start a new wildfire scenario with automatic progression."""
        user_state = self.get_user_state(user_id)
        
        # Create new fire grid simulation
        grid_size = 6 if difficulty == "easy" else 8 if difficulty == "hard" else 7
        user_state["fire_grid"] = FireGrid(size=grid_size)
        user_state["incident_name"] = self.report_generator.generate_incident_name()
        user_state["game_phase"] = "active"
        user_state["last_update"] = datetime.now()
        user_state["next_progression"] = datetime.now() + timedelta(seconds=45)  # Auto-advance in 45 seconds
        user_state["resources_deployed"] = {"hand_crews": 1, "engines": 1, "air_tankers": 0}
        user_state["budget"] = 15  # Starting budget
        user_state["performance_score"] = 100  # Performance rating
        user_state["actions_taken"] = 0
        
        # Start the fire
        fire_intensity = "low" if difficulty == "easy" else "high" if difficulty == "hard" else "moderate"
        user_state["fire_grid"].start_fire(intensity=fire_intensity)
        
        return user_state
            
    def deploy_resources(self, user_id, resource_type, count):
        """Deploy additional resources to the incident."""
        user_state = self.get_user_state(user_id)
        
        # Check for auto-progression first
        auto_result = self.check_auto_progression(user_id)
        
        if user_state["game_phase"] != "active":
            return {"success": False, "reason": "no_active_incident"}
            
        # Resource costs - SPENDING points on resources
        costs = {"hand_crews": 2, "engines": 3, "air_tankers": 5}
        cost = costs.get(resource_type, 2) * count
        
        if user_state["budget"] < cost:
            return {"success": False, "reason": "insufficient_budget", "cost": cost, "budget": user_state["budget"]}
            
        if resource_type in user_state["resources_deployed"]:
            user_state["resources_deployed"][resource_type] += count
            user_state["budget"] -= cost  # SPEND points
            user_state["actions_taken"] += 1
            
            # Apply immediate suppression effect
            self._apply_immediate_suppression(user_state, resource_type, count)
            
            return {
                "success": True, 
                "cost": cost, 
                "remaining_budget": user_state["budget"],
                "auto_progression": auto_result
            }
        
        return {"success": False, "reason": "invalid_resource"}
    
    def check_auto_progression(self, user_id):
        """Check if fire should automatically progress."""
        user_state = self.get_user_state(user_id)
        
        if user_state["game_phase"] != "active" or not user_state.get("next_progression"):
            return None
            
        if datetime.now() >= user_state["next_progression"]:
            return self.auto_advance_fire(user_id)
        
        return None
    
    def auto_advance_fire(self, user_id):
        """Automatically advance fire and award/deduct points based on performance."""
        user_state = self.get_user_state(user_id)
        
        if not user_state["fire_grid"]:
            return None
            
        # Get stats before progression
        old_stats = user_state["fire_grid"].get_fire_statistics()
        
        # Apply suppression based on deployed resources
        total_suppression = (
            user_state["resources_deployed"]["hand_crews"] * 20 +
            user_state["resources_deployed"]["engines"] * 15 + 
            user_state["resources_deployed"]["air_tankers"] * 30
        )
        
        user_state["fire_grid"].apply_suppression(total_suppression)
        user_state["fire_grid"].advance_operational_period()
        
        # Get stats after progression
        new_stats = user_state["fire_grid"].get_fire_statistics()
        
        # Calculate performance and award/deduct points
        containment_improvement = new_stats['containment_percent'] - old_stats['containment_percent']
        size_growth = new_stats['fire_size_acres'] - old_stats['fire_size_acres']
        
        # EARN points for good performance
        points_earned = 0
        if containment_improvement > 20:
            points_earned = 8  # Excellent containment
        elif containment_improvement > 10:
            points_earned = 5  # Good progress
        elif containment_improvement > 0:
            points_earned = 3  # Some progress
        else:
            points_earned = 1  # Minimal progress
            
        # Lose points for fire growth
        if size_growth > 30:
            points_earned -= 3  # Fire grew significantly
        elif size_growth > 15:
            points_earned -= 1  # Some growth
            
        user_state["budget"] += max(points_earned, 0)  # EARN points for performance
        user_state["performance_score"] += points_earned * 2
        user_state["next_progression"] = datetime.now() + timedelta(seconds=45)  # Next auto-advance
        
        # Check if fire is contained or critical
        if user_state["fire_grid"].is_contained():
            user_state["game_phase"] = "contained"
        elif new_stats['fire_size_acres'] >= 200:
            user_state["game_phase"] = "critical_failure"
            
        return {
            "containment_change": containment_improvement,
            "size_change": size_growth,
            "points_earned": points_earned,
            "new_budget": user_state["budget"],
            "new_stats": new_stats
        }
    
    def _apply_immediate_suppression(self, user_state, resource_type, count):
        """Apply immediate suppression effect when resources are deployed."""
        suppression_values = {"hand_crews": 5, "engines": 7, "air_tankers": 12}
        immediate_suppression = suppression_values.get(resource_type, 5) * count
        user_state["fire_grid"].apply_suppression(immediate_suppression)
        
    def advance_operational_period(self, user_id):
        """Advance to next operational period with fire progression."""
        user_state = self.get_user_state(user_id)
        
        if not user_state["fire_grid"] or user_state["game_phase"] != "active":
            return None
            
        # Apply suppression based on deployed resources
        total_suppression = (
            user_state["resources_deployed"]["hand_crews"] * 20 +
            user_state["resources_deployed"]["engines"] * 15 + 
            user_state["resources_deployed"]["air_tankers"] * 30
        )
        
        user_state["fire_grid"].apply_suppression(total_suppression)
        user_state["fire_grid"].advance_operational_period()
        user_state["last_update"] = datetime.now()
        
        # Check if fire is contained
        if user_state["fire_grid"].is_contained():
            user_state["game_phase"] = "contained"
            
        return user_state["fire_grid"].get_fire_statistics()
        
    def get_current_status(self, user_id):
        """Get current fire status and statistics."""
        user_state = self.get_user_state(user_id)
        
        if not user_state["fire_grid"]:
            return None
            
        return user_state["fire_grid"].get_fire_statistics()
        
    def generate_incident_report(self, user_id, report_type="briefing"):
        """Generate professional incident report."""
        user_state = self.get_user_state(user_id)
        
        if not user_state["fire_grid"] or not user_state["incident_name"]:
            return "No active incident to report."
            
        if report_type == "initial":
            return self.report_generator.generate_initial_dispatch_report(
                user_state["fire_grid"], user_state["incident_name"]
            )
        elif report_type == "briefing":
            return self.report_generator.generate_operational_briefing(
                user_state["fire_grid"], user_state["incident_name"]
            )
        elif report_type == "status":
            return self.report_generator.generate_situation_update(
                user_state["fire_grid"], user_state["incident_name"]
            )
        elif report_type == "resources":
            return self.report_generator.generate_resource_status_report(
                user_state["resources_deployed"]
            )
        elif report_type == "final":
            final_stats = user_state["fire_grid"].get_fire_statistics()
            return self.report_generator.generate_after_action_report(
                user_state["fire_grid"], user_state["incident_name"], final_stats
            )
        else:
            return "Unknown report type requested."


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
        self.auto_progression_task = None
        
    @commands.Cog.listener()
    async def on_ready(self):
        """Bot startup handler."""
        await self.bot.change_presence(activity=discord.Game(name="🔥 Wildfire Response MMORPG"))
        
        # Debug command tree state
        commands_in_tree = [cmd.name for cmd in self.bot.tree.get_commands()]
        print(f"🔥 Commands in tree: {commands_in_tree}")
        
        # Sync commands globally first for DM usage
        try:
            global_synced = await self.bot.tree.sync()
            print(f"🔥 Synced {len(global_synced)} commands globally")
            
            # Copy global commands to each guild then sync
            total_synced = 0
            for guild in self.bot.guilds:
                # Copy global commands to this guild
                self.bot.tree.copy_global_to(guild=guild)
                
                # Now sync guild-specific commands (includes copied globals)
                synced = await self.bot.tree.sync(guild=guild)
                total_synced += len(synced)
                print(f"🔥 Synced {len(synced)} commands to guild {guild.name}")
                
            print(f"🔥 Total {total_synced} guild commands synced")
        except Exception as e:
            print(f"Failed to sync commands: {e}")
            
        print(f"🔥 Wildfire bot online in {len(self.bot.guilds)} servers")
        
        # Start auto-progression background task
        if not self.auto_progression_task or self.auto_progression_task.done():
            self.auto_progression_task = asyncio.create_task(self._auto_progression_loop())
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle typed tactical choices like '1', '2', '3'."""
        # Ignore bot messages and guild messages
        if message.author.bot or message.guild is not None:
            return
            
        # Check if user has active incident
        user_state = self.singleplayer_game.get_user_state(message.author.id)
        if user_state["game_phase"] != "active":
            return
            
        # Handle numbered choices
        if message.content.strip() in ["1", "1️⃣"]:
            result = self.singleplayer_game.deploy_resources(message.author.id, "hand_crews", 1)
            await self._send_choice_response(message.channel, "Ground Crews", result, message.author.id)
        elif message.content.strip() in ["2", "2️⃣"]:
            result = self.singleplayer_game.deploy_resources(message.author.id, "air_tankers", 1)
            await self._send_choice_response(message.channel, "Air Support", result, message.author.id)
        elif message.content.strip() in ["3", "3️⃣"]:
            result = self.singleplayer_game.deploy_resources(message.author.id, "engines", 1)
            await self._send_choice_response(message.channel, "Engine Company", result, message.author.id)
    
    async def _send_choice_response(self, channel, resource_name, result, user_id):
        """Send response for typed tactical choice."""
        if result["success"]:
            # Show auto-progression result if it happened
            auto = result.get("auto_progression")
            auto_message = ""
            if auto:
                if auto["points_earned"] > 0:
                    auto_message = f"\n\n📈 **PERFORMANCE BONUS: +{auto['points_earned']} pts!**\nGreat containment work!"
                else:
                    auto_message = f"\n\n📉 **FIRE SPREADING!**\nNeed more suppression - deploy fast!"
            
            # Get current fire status after deployment
            user_state = self.singleplayer_game.get_user_state(user_id)
            stats = user_state["fire_grid"].get_fire_statistics()
            threats = user_state["fire_grid"].get_threat_assessment()
            
            threat_emoji = "🔴" if threats['threat_level'] == "HIGH" else "🟡" if threats['threat_level'] == "MODERATE" else "🟢"
            
            message = f"""🚒 **{resource_name.upper()} DEPLOYED!**


🔥 **CURRENT FIRE STATUS:**
• **Size:** {stats['fire_size_acres']} acres
• **Containment:** {stats['containment_percent']}%
• **Threat:** {threat_emoji} {threats['threat_level']} - {threats['threatened_structures']} structures at risk


💰 **Budget:** {result['remaining_budget']} points remaining
{auto_message}


**Continue fighting the fire:**"""
            
            # Create new tactical choices view
            view = TacticalChoicesView(self.singleplayer_game, user_id)
            await channel.send(message, view=view)
            
        else:
            message = f"""❌ **INSUFFICIENT BUDGET**

**Need {result['cost']} pts, have {result['budget']} pts**

💡 **EARN MORE POINTS:** Good containment = more budget!
Try **Ground Crews** (2 pts) - most cost-effective option."""
            
            await channel.send(message)
        
    @discord.app_commands.command(name="fire", description="Report a new wildfire incident")
    async def fire_command(self, interaction: discord.Interaction):
        """Create new wildfire incident - context-aware for DM vs Guild."""
        if interaction.guild is None:
            await self._handle_singleplayer_fire(interaction)
        else:
            await self._handle_multiplayer_fire(interaction)
            
    async def _handle_singleplayer_fire(self, interaction: discord.Interaction):
        """Handle fire creation in DM (singleplayer mode)."""
        user_state = self.singleplayer_game.get_user_state(interaction.user.id)
        
        if user_state["game_phase"] == "active":
            # Already have an active incident
            stats = self.singleplayer_game.get_current_status(interaction.user.id)
            embed = discord.Embed(
                title="🔥 INCIDENT ALREADY ACTIVE",
                description=f"You are currently managing **{user_state['incident_name']}**",
                color=0xFF6B35
            )
            
            embed.add_field(
                name="📊 Current Status",
                value=f"**Fire Size:** {stats['fire_size_acres']} acres\n"
                      f"**Containment:** {stats['containment_percent']}%\n"
                      f"**Operational Period:** {stats['operational_period']}",
                inline=False
            )
            
            embed.add_field(
                name="⚡ Available Actions",
                value="• `/respond` - Deploy additional resources\n"
                      "• `/advance` - Progress to next operational period\n"
                      "• `/firestatus` - Get situation reports\n"
                      "• `/stop` - End current scenario",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
        else:
            # No active incident - redirect to /start
            embed = discord.Embed(
                title="🎯 START YOUR WILDFIRE TRAINING",
                description="For the full Incident Commander experience, use **`/start`** to begin a complete wildfire scenario.",
                color=0xFF4500
            )
            
            embed.add_field(
                name="🌟 Enhanced Experience",
                value="• **Realistic fire simulation** with weather and terrain\n"
                      "• **Authentic ICS reports** and operational briefings\n"
                      "• **Progressive difficulty** with tactical challenges\n"
                      "• **Complete scenario arc** from dispatch to after-action",
                inline=False
            )
            
            embed.add_field(
                name="🚀 Get Started",
                value="Use `/start` to begin your Incident Commander training!",
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
        
        if user_state["game_phase"] != "active":
            await interaction.response.send_message(
                "❌ No active incident. Use `/start` to begin a wildfire scenario.",
                ephemeral=True
            )
            return
            
        # Deploy additional resources to the incident
        resource_deployed = random.choice(["hand_crews", "engines", "air_tankers"])
        result = self.singleplayer_game.deploy_resources(interaction.user.id, resource_deployed, 1)
        
        if result["success"]:
            resource_names = {
                "hand_crews": "Hand Crew",
                "engines": "Engine Company", 
                "air_tankers": "Air Tanker"
            }
            
            embed = discord.Embed(
                title="🚒 RESOURCES DEPLOYED",
                description=f"**{resource_names[resource_deployed]}** deployed to {user_state['incident_name']}",
                color=0x00AA00
            )
            
            embed.add_field(
                name="💰 COST",
                value=f"**-{result['cost']} pts** (Budget: {result['remaining_budget']} pts remaining)",
                inline=True
            )
            
            # Get current status for display
            stats = self.singleplayer_game.get_current_status(interaction.user.id)
            if stats:
                embed.add_field(
                    name="🔥 FIRE STATUS",
                    value=f"**{stats['fire_size_acres']} acres** • **{stats['containment_percent']}%** contained",
                    inline=True
                )
                
            embed.add_field(
                name="⚡ NEXT",
                value="Use `/advance` to see what happens",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
        else:
            # Handle failure cases with specific messages
            if result["reason"] == "insufficient_budget":
                await interaction.response.send_message(
                    f"❌ **INSUFFICIENT BUDGET**\n"
                    f"Need {result['cost']} pts, you have {result['budget']} pts\n"
                    f"💡 Use `/advance` to progress and potentially get more budget",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "❌ Unable to deploy resources at this time", ephemeral=True
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
        
        if user_state["game_phase"] == "ready":
            await interaction.response.send_message(
                "📍 No active incident. Use `/start` to begin a wildfire scenario.", 
                ephemeral=True
            )
            return
            
        # Generate situation update report
        status_report = self.singleplayer_game.generate_incident_report(
            interaction.user.id, "status"
        )
        
        await interaction.response.send_message(f"```{status_report}```")
        
    async def _handle_multiplayer_status(self, interaction: discord.Interaction):
        """Handle status display in Guild (multiplayer mode)."""
        if not self.game.active_fires:
            await interaction.response.send_message(
                "📍 No active fires currently", ephemeral=True
            )
            return
            
        embed = self._create_guild_status_embed()
        await interaction.response.send_message(embed=embed)
        
        
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
        
    @discord.app_commands.command(name="start", description="🚀 Begin new wildfire incident command scenario (DM only)")
    async def start_command(self, interaction: discord.Interaction):
        """Start compelling wildfire scenario with full simulation."""
        if interaction.guild is not None:
            await interaction.response.send_message(
                "❌ Singleplayer scenarios only work in DM", ephemeral=True
            )
            return
            
        # Start new scenario with realistic simulation
        user_state = self.singleplayer_game.start_new_scenario(interaction.user.id)
        
        # Generate initial dispatch report
        initial_report = self.singleplayer_game.generate_incident_report(
            interaction.user.id, "initial"
        )
        
        # Immediate dispatch - drop straight into the fire with readable text
        dispatch_message = await self._create_dispatch_message(interaction.user.id)
        view = TacticalChoicesView(self.singleplayer_game, interaction.user.id)
        await interaction.response.send_message(dispatch_message, view=view)
        
    @discord.app_commands.command(name="stop", description="🛑 End current session (DM only)")
    async def stop_command(self, interaction: discord.Interaction):
        """End current singleplayer session cleanly."""
        if interaction.guild is not None:
            await interaction.response.send_message(
                "❌ Debug commands only work in DM", ephemeral=True
            )
            return
            
        user_state = self.singleplayer_game.get_user_state(interaction.user.id)
        
        # Generate final report if there was an active incident
        if user_state.get("fire_grid") and user_state.get("incident_name"):
            final_report = self.singleplayer_game.generate_incident_report(
                interaction.user.id, "final"
            )
            await interaction.response.send_message(f"```{final_report}```")
        else:
            await interaction.response.send_message("🏁 **Session Ended**\nUse `/start` to begin a new scenario.")
        
        # Clear the state
        self.singleplayer_game.clear_user_state(interaction.user.id)
        
    @discord.app_commands.command(name="advance", description="⏰ Advance to next operational period (DM only)")
    async def advance_command(self, interaction: discord.Interaction):
        """Advance operational period with fire progression."""
        if interaction.guild is not None:
            await interaction.response.send_message(
                "❌ Operational commands only work in DM", ephemeral=True
            )
            return
            
        stats = self.singleplayer_game.advance_operational_period(interaction.user.id)
        
        if not stats:
            await interaction.response.send_message(
                "❌ No active incident. Use `/start` to begin a scenario.", ephemeral=True
            )
            return
            
        # Generate operational briefing
        briefing = self.singleplayer_game.generate_incident_report(
            interaction.user.id, "briefing"
        )
        
        # Send operational briefing as readable text with tactical choices
        briefing_message = await self._create_operational_message(interaction.user.id)
        view = TacticalChoicesView(self.singleplayer_game, interaction.user.id)
        await interaction.response.send_message(briefing_message, view=view)
        
        # Check if fire is contained
        user_state = self.singleplayer_game.get_user_state(interaction.user.id)
        if user_state["game_phase"] == "contained":
            await interaction.followup.send(
                "🎉 **FIRE CONTAINED!** Excellent work, Incident Commander!\n"
                "Use `/stop` to see your after-action report."
            )
            
    @discord.app_commands.command(name="report", description="📋 Request specific incident reports (DM only)")
    @discord.app_commands.describe(
        report_type="Type of report to generate"
    )
    @discord.app_commands.choices(report_type=[
        discord.app_commands.Choice(name="📋 Operational Briefing", value="briefing"),
        discord.app_commands.Choice(name="📢 Situation Update", value="status"), 
        discord.app_commands.Choice(name="👥 Resource Status", value="resources"),
        discord.app_commands.Choice(name="🚨 Initial Dispatch", value="initial")
    ])
    async def report_command(self, interaction: discord.Interaction, report_type: str):
        """Generate specific incident report types."""
        if interaction.guild is not None:
            await interaction.response.send_message(
                "❌ Report commands only work in DM", ephemeral=True
            )
            return
            
        report = self.singleplayer_game.generate_incident_report(
            interaction.user.id, report_type
        )
        
        if "No active incident" in report:
            await interaction.response.send_message(
                "❌ No active incident to report. Use `/start` to begin a scenario.", 
                ephemeral=True
            )
            return
            
        await interaction.response.send_message(f"```{report}```")
        
    async def _create_dispatch_message(self, user_id) -> str:
        """Create readable text message for initial dispatch."""
        user_state = self.singleplayer_game.get_user_state(user_id)
        
        if not user_state["fire_grid"]:
            return "❌ **ERROR** - No active incident"
            
        # Get fire statistics and threat data
        stats = user_state["fire_grid"].get_fire_statistics()
        threats = user_state["fire_grid"].get_threat_assessment()
        incident_name = user_state["incident_name"]
        
        # Determine threat level styling
        threat_emoji = "🔴" if threats['threat_level'] == "HIGH" else "🟡" if threats['threat_level'] == "MODERATE" else "🟢"
        
        # Create clear, scannable message
        message = f"""🚨 **WILDFIRE EMERGENCY** 🚨

**{incident_name.upper()}** is spreading!


🔥 **FIRE STATUS:**
• **Size:** {stats['fire_size_acres']} acres
• **Containment:** {stats['containment_percent']}%
• **Threat:** {threat_emoji} {threats['threat_level']} - {threats['threatened_structures']} structures at risk
• **Weather:** {stats['weather']['wind_direction']} {stats['weather']['wind_speed']} mph, {stats['weather']['temperature']}°F


💰 **Budget:** {user_state.get('budget', 15)} points
*Good containment earns more points!*


**TACTICAL DEPLOYMENT OPTIONS:**

1️⃣ **Ground Crews** (2 pts) - **FAST ATTACK**
   • Quick response, cost-effective
   • Best for: Small fires, initial attack

2️⃣ **Air Support** (5 pts) - **HEAVY POWER** 
   • Maximum suppression, expensive
   • Best for: Large fires, difficult terrain

3️⃣ **Engine Company** (3 pts) - **BALANCED OPTION**
   • Moderate cost, reliable suppression
   • Best for: Structure protection, sustained attack


🎯 **GOAL:** Contain fire before it reaches 200 acres!

**Click buttons below OR type 1, 2, or 3 to deploy!**"""

        return message
    
    async def _create_operational_message(self, user_id) -> str:
        """Create readable text message for operational briefing."""
        user_state = self.singleplayer_game.get_user_state(user_id)
        
        if not user_state["fire_grid"]:
            return "❌ **No active fire**"
            
        stats = user_state["fire_grid"].get_fire_statistics()
        threats = user_state["fire_grid"].get_threat_assessment()
        incident_name = user_state["incident_name"]
        
        # Determine urgency level
        if stats['fire_size_acres'] > 100:
            urgency_icon = "🚨"
            urgency_text = "CRITICAL"
        elif stats['fire_size_acres'] > 50:
            urgency_icon = "⚠️"
            urgency_text = "HIGH PRIORITY"
        else:
            urgency_icon = "🔥"
            urgency_text = "ACTIVE"
        
        # Fire status trend
        size_change = "📈 GROWING FAST" if stats['active_cells'] > 2 else "📉 Slowing down" if stats['active_cells'] == 0 else "🔥 Still active"
        threat_emoji = "🔴" if threats['threat_level'] == "HIGH" else "🟡" if threats['threat_level'] == "MODERATE" else "🟢"
        
        # Auto-progression timer
        next_update = user_state.get("next_progression")
        time_left = ""
        if next_update:
            seconds_left = max(0, int((next_update - datetime.now()).total_seconds()))
            time_left = f"⏰ **Auto-update in {seconds_left} seconds**"
        
        # Check if contained
        if stats['containment_percent'] >= 100:
            message = f"""🎉 **FIRE CONTAINED!** 🎉

**{incident_name.upper()}** has been successfully contained!

🔥 **Final size:** {stats['fire_size_acres']} acres
✅ **100% contained**

**Excellent work, Incident Commander!**
Use `/stop` to see your performance report."""
        else:
            message = f"""{urgency_icon} **{incident_name.upper()}** - {urgency_text}


🔥 **FIRE STATUS:**
• **Size:** {stats['fire_size_acres']} acres ({size_change})
• **Containment:** {stats['containment_percent']}%
• **Threat:** {threat_emoji} {threats['threat_level']} - Wind: {stats['weather']['wind_speed']} mph


💰 **Budget:** {user_state.get('budget', 10)} points


**TACTICAL OPTIONS:**
1️⃣ **Ground Crews** (2 pts) - Fast attack
2️⃣ **Air Support** (5 pts) - Heavy power 
3️⃣ **Engine Company** (3 pts) - Balanced

{time_left}

🎯 **Contain before 200 acres!**"""
        
        return message
    
    async def _auto_progression_loop(self):
        """Background task that automatically progresses fires and sends updates."""
        while True:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                # Check all active user states
                for user_id, user_state in list(self.singleplayer_game.user_states.items()):
                    if user_state["game_phase"] != "active":
                        continue
                        
                    next_progression = user_state.get("next_progression")
                    if not next_progression:
                        continue
                        
                    # Check if it's time for auto-progression
                    if datetime.now() >= next_progression:
                        try:
                            # Get user from Discord
                            user = self.bot.get_user(user_id)
                            if not user:
                                continue
                                
                            # Auto-advance the fire
                            auto_result = self.singleplayer_game.auto_advance_fire(user_id)
                            if not auto_result:
                                continue
                                
                            # Send status update
                            status_message = await self._create_operational_message(user_id)
                            view = TacticalChoicesView(self.singleplayer_game, user_id)
                            
                            # Send to user's DM
                            try:
                                await user.send(status_message, view=view)
                            except discord.Forbidden:
                                # User has DMs disabled, skip
                                pass
                                
                        except Exception as e:
                            print(f"Error in auto-progression for user {user_id}: {e}")
                            
            except Exception as e:
                print(f"Error in auto-progression loop: {e}")
                await asyncio.sleep(30)  # Wait longer on error


async def setup_wildfire_commands(bot):
    """
    @brief Add wildfire commands to existing bot
    @details Context-aware commands for both DM and Guild modes
    """
    await bot.add_cog(WildfireCommands(bot))
    print("🔥 Wildfire commands cog loaded - syncing will happen on ready")