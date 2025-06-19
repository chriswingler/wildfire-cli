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


class TeamTacticalChoicesView(discord.ui.View):
    """Interactive button choices for team tactical decisions."""
    
    def __init__(self, game, fire_id, user_id):
        super().__init__(timeout=300)  # 5 minute timeout
        self.game = game
        self.fire_id = fire_id
        self.user_id = user_id
    
    @discord.ui.button(label='1 🚒 $2k', style=discord.ButtonStyle.primary, custom_id='deploy_team_crews')
    async def deploy_crews(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your deployment!", ephemeral=True)
            return
            
        result = self.game.deploy_team_resources(self.fire_id, self.user_id, "hand_crews", 1)
        await self._handle_team_choice_result(interaction, "Ground Crews", result)
    
    @discord.ui.button(label='2 🚁 $5k', style=discord.ButtonStyle.danger, custom_id='deploy_team_air')
    async def deploy_air(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your deployment!", ephemeral=True)
            return
            
        result = self.game.deploy_team_resources(self.fire_id, self.user_id, "air_tankers", 1)
        await self._handle_team_choice_result(interaction, "Air Support", result)
    
    @discord.ui.button(label='3 🚛 $3k', style=discord.ButtonStyle.secondary, custom_id='deploy_team_engines')
    async def deploy_engines(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your deployment!", ephemeral=True)
            return
            
        result = self.game.deploy_team_resources(self.fire_id, self.user_id, "engines", 1)
        await self._handle_team_choice_result(interaction, "Engine Company", result)
    
    @discord.ui.button(label='4 🚜 $4k', style=discord.ButtonStyle.success, custom_id='deploy_team_dozers')
    async def deploy_dozers(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your deployment!", ephemeral=True)
            return
            
        result = self.game.deploy_team_resources(self.fire_id, self.user_id, "dozers", 1)
        await self._handle_team_choice_result(interaction, "Dozer", result)
    
    async def _handle_team_choice_result(self, interaction, resource_name, result):
        """Handle the result of a team tactical choice."""
        try:
            if result["success"]:
                # Show auto-progression if it happened
                auto = result.get("auto_progression")
                auto_message = ""
                if auto:
                    if auto["budget_earned"] > 0:
                        auto_message = f"\n\n📈 **TEAM BONUS: +${auto['budget_earned']}k budget!**\nExcellent team coordination!"
                    else:
                        auto_message = f"\n\n📉 **FIRE SPREADING!**\nTeam needs more suppression - deploy fast!"
                
                # Get current fire status after deployment
                fire_status = self.game.get_fire_status(self.fire_id)
                threat_emoji = "🔴" if fire_status['threat_level'] in ["HIGH", "EXTREME"] else "🟡" if fire_status['threat_level'] == "MODERATE" else "🟢"
                
                message = f"""🚒 **{resource_name.upper()} DEPLOYED BY TEAM!**

👤 **{interaction.user.display_name}** deployed {resource_name} to **{fire_status['incident_name']}**

🔥 **TEAM FIRE STATUS:**
• **Size:** {fire_status['fire_size_acres']} acres
• **Containment:** {fire_status['containment_percent']}%
• **Threat:** {threat_emoji} {fire_status['threat_level']} - {fire_status['threatened_structures']} structures at risk

👥 **TEAM RESOURCES:**
• **Ground Crews:** {fire_status['resources_deployed']['hand_crews']} units
• **Engines:** {fire_status['resources_deployed']['engines']} units
• **Air Support:** {fire_status['resources_deployed']['air_tankers']} units
• **Dozers:** {fire_status['resources_deployed']['dozers']} units

💰 **Team Budget:** ${fire_status['team_budget']}k remaining
{auto_message}

**Team members continue using `/respond` to deploy more resources!**"""
                
                # Check for mission accomplished (100% containment)
                if fire_status["status"] == "contained":
                    message = f"""🎉 **MISSION ACCOMPLISHED - TEAM SUCCESS!**

🏆 **{fire_status['incident_name'].upper()} CONTAINED BY TEAM!**

✅ **FINAL TEAM STATUS:**
• **Size:** {fire_status['fire_size_acres']} acres
• **Containment:** 100%
• **Team Budget:** ${fire_status['team_budget']}k remaining

🚒 **OUTSTANDING TEAMWORK!** Your coordinated effort successfully contained the fire!

**Ready for the next challenge? Use `/fire` to start another team response!**"""
                
                elif fire_status["status"] == "critical_failure":
                    message = f"""💥 **TEAM MISSION FAILED - FIRE OUT OF CONTROL!**

🚨 **{fire_status['incident_name'].upper()} - EVACUATION ORDERED!**

❌ **FINAL TEAM STATUS:**
• **Size:** {fire_status['fire_size_acres']} acres (OVER 200 ACRES)
• **Containment:** {fire_status['containment_percent']}%
• **Team Budget:** ${fire_status['team_budget']}k remaining

⚠️ **FIRE TOO LARGE** - Team coordination wasn't enough to stop the spread!

**Learn and improve! Use `/fire` to try another team response.**"""
                
                await interaction.response.send_message(message)
                
            else:
                # Not enough budget or other error
                if "Insufficient team budget" in result.get("error", ""):
                    message = f"""💰 **INSUFFICIENT TEAM BUDGET!**

❌ **{resource_name} deployment failed**
• **Cost:** ${result['cost']}k
• **Team Budget:** ${result['budget']}k available

**Team needs to coordinate better or wait for budget from fire suppression progress!**
Use `/firestatus` to check current team resources."""
                else:
                    message = f"❌ **Deployment failed:** {result.get('error', 'Unknown error')}"
                
                await interaction.response.send_message(message, ephemeral=True)
                
        except Exception as e:
            print(f"Error in team choice handling: {e}")
            await interaction.response.send_message("❌ Error processing team deployment", ephemeral=True)


class TacticalChoicesView(discord.ui.View):
    """Interactive button choices for tactical decisions."""
    
    def __init__(self, singleplayer_game, user_id):
        super().__init__(timeout=300)  # 5 minute timeout
        self.singleplayer_game = singleplayer_game
        self.user_id = user_id
    
    @discord.ui.button(label='1 🚒 $1.8k', style=discord.ButtonStyle.primary, custom_id='deploy_crews')
    async def deploy_crews(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your incident!", ephemeral=True)
            return
            
        result = self.singleplayer_game.deploy_resources(self.user_id, "hand_crews", 1)
        await self._handle_choice_result(interaction, "Ground Crews", result)
    
    @discord.ui.button(label='2 🚁 $12k', style=discord.ButtonStyle.danger, custom_id='deploy_air')
    async def deploy_air(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your incident!", ephemeral=True)
            return
            
        result = self.singleplayer_game.deploy_resources(self.user_id, "air_tankers", 1)
        await self._handle_choice_result(interaction, "Air Support", result)
    
    @discord.ui.button(label='3 🚛 $3.2k', style=discord.ButtonStyle.secondary, custom_id='deploy_engines')
    async def deploy_engines(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your incident!", ephemeral=True)
            return
            
        result = self.singleplayer_game.deploy_resources(self.user_id, "engines", 1)
        await self._handle_choice_result(interaction, "Engine Company", result)
    
    @discord.ui.button(label='4 🚜 $4.6k', style=discord.ButtonStyle.success, custom_id='deploy_dozers')
    async def deploy_dozers(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This isn't your incident!", ephemeral=True)
            return
            
        result = self.singleplayer_game.deploy_resources(self.user_id, "dozers", 1)
        await self._handle_choice_result(interaction, "Dozer", result)
    
    async def _handle_choice_result(self, interaction, resource_name, result):
        """Handle the result of a tactical choice."""
        try:
            if result["success"]:
                # Show auto-progression if it happened
                auto = result.get("auto_progression")
                auto_message = ""
                if auto:
                    if auto["points_earned"] > 0:
                        auto_message = f"\n\n📈 **PERFORMANCE BONUS: +{auto['points_earned']} pts!**\nGreat containment work!"
                    else:
                        auto_message = f"\n\n📉 **FIRE SPREADING!**\nNeed more suppression - deploy fast!"
                
                # Generate progression comparison
                progression_message = self._create_progression_message(result)
                
                # Get current fire status after deployment
                user_state = self.singleplayer_game.get_user_state(self.user_id)
                stats = user_state["fire_grid"].get_fire_statistics()
                threats = user_state["fire_grid"].get_threat_assessment()
                
                threat_emoji = "🔴" if threats['threat_level'] in ["HIGH", "EXTREME"] else "🟡" if threats['threat_level'] == "MODERATE" else "🟢"
                
                message = f"""🚒 **{resource_name.upper()} DEPLOYED!**

{progression_message}

🔥 **CURRENT FIRE STATUS:**
• **Size:** {stats['fire_size_acres']} acres
• **Containment:** {stats['containment_percent']}%
• **Threat:** {threat_emoji} {threats['threat_level']} - {threats['threatened_structures']} structures at risk

💰 **Budget:** ${result['remaining_budget']:,} remaining
{auto_message}

**Continue fighting the fire:**"""
                
                # Check for mission accomplished (100% containment)
                user_state = self.singleplayer_game.get_user_state(self.user_id)
                current_budget = user_state["budget"]
                
                if stats['containment_percent'] >= 100:
                    # Mission accomplished! Award budget and start new fire
                    bonus_budget = 8000  # Reward for successful containment
                    user_state["budget"] += bonus_budget
                    new_budget = user_state["budget"]
                    
                    # Start new fire immediately
                    user_state = self.singleplayer_game.start_new_scenario(self.user_id)
                    new_stats = user_state["fire_grid"].get_fire_statistics()
                    new_threats = user_state["fire_grid"].get_threat_assessment()
                    new_threat_emoji = "🔴" if new_threats['threat_level'] in ["HIGH", "EXTREME"] else "🟡" if new_threats['threat_level'] == "MODERATE" else "🟢"
                    
                    mission_message = f"""🎉 **MISSION ACCOMPLISHED!** 🎉

🔥 **PREVIOUS FIRE:** Successfully contained at {after['fire_size_acres']} acres
💰 **PERFORMANCE BONUS:** +${bonus_budget:,} 
💳 **NEW BUDGET:** ${new_budget:,}

🚨 **NEW WILDFIRE DETECTED!**

**{user_state['incident_name'].upper()}** is spreading!

🔥 **FIRE STATUS:**
• **Size:** {new_stats['fire_size_acres']} acres
• **Containment:** {new_stats['containment_percent']}%
• **Threat:** {new_threat_emoji} {new_threats['threat_level']} - {new_threats['threatened_structures']} structures at risk

💰 **Budget:** ${new_budget:,}

**Ready for your next incident command assignment:**"""
                    
                    # Create new tactical choices view
                    view = TacticalChoicesView(self.singleplayer_game, self.user_id)
                    
                    # Use defer + followup for clean DM conversation (no reply chains)
                    if interaction.guild is None:
                        await interaction.response.defer()
                        await interaction.followup.send(mission_message, view=view)
                    else:
                        await interaction.response.send_message(mission_message, view=view)
                    return
                
                # Check if user can afford any resources before showing choices
                min_cost = min([1800, 3200, 4600, 12000])  # hand_crews is cheapest
                
                if current_budget < min_cost:
                    # Game over - can't afford any resources
                    game_over_message = f"""💥 **GAME OVER - INSUFFICIENT FUNDING!**

🔥 **FINAL SITUATION:**
• **Fire Size:** {stats['fire_size_acres']} acres
• **Containment:** {stats['containment_percent']}%
• **Budget Remaining:** ${current_budget:,}

🎯 **RESULT:** Unable to deploy additional resources. Fire continues to spread unchecked.

**💡 Lesson Learned:** Budget management is critical in incident command!

**🚀 Use `/start` to try again with better resource allocation!**"""
                    
                    # Use defer + followup for clean DM conversation (no reply chains)  
                    if interaction.guild is None:
                        await interaction.response.defer()
                        await interaction.followup.send(game_over_message)
                    else:
                        await interaction.response.send_message(game_over_message)
                else:
                    # Create new tactical choices view
                    view = TacticalChoicesView(self.singleplayer_game, self.user_id)
                    
                    # Use defer + followup for clean DM conversation (no reply chains)
                    if interaction.guild is None:
                        await interaction.response.defer()
                        await interaction.followup.send(message, view=view)
                    else:
                        await interaction.response.send_message(message, view=view)
            else:
                # Game over - no more budget
                user_state = self.singleplayer_game.get_user_state(self.user_id)
                stats = user_state["fire_grid"].get_fire_statistics()
                
                # Set game phase to failed
                user_state["game_phase"] = "failed"
                
                message = f"""💥 **GAME OVER - OUT OF BUDGET!**

🔥 **FINAL FIRE STATUS:**
• **Size:** {stats['fire_size_acres']} acres
• **Containment:** {stats['containment_percent']}%

💰 **Budget:** ${result['budget']:,} (Need ${result['cost']:,} for {resource_name})

🎯 **RESULT:** Fire continued to spread without sufficient resources!

**🚀 Ready to try again?**"""
                
                # Use defer + followup for clean DM conversation (no reply chains)
                if interaction.guild is None:
                    await interaction.response.defer()
                    await interaction.followup.send(message)
                else:
                    await interaction.response.send_message(message)
        except Exception as e:
            print(f"Error in _handle_choice_result: {e}")
            # Show basic tactical update even on error
            user_state = self.singleplayer_game.get_user_state(self.user_id)
            stats = user_state["fire_grid"].get_fire_statistics()
            threats = user_state["fire_grid"].get_threat_assessment()
            
            threat_emoji = "🔴" if threats['threat_level'] in ["HIGH", "EXTREME"] else "🟡" if threats['threat_level'] == "MODERATE" else "🟢"
            
            message = f"""🚒 **{resource_name.upper()} DEPLOYED!**

🔥 **FIRE UPDATE:**
• **Size:** {stats['fire_size_acres']} acres
• **Containment:** {stats['containment_percent']}%
• **Threat:** {threat_emoji} {threats['threat_level']}

💰 **Budget:** ${user_state.get('budget', 20000):,} remaining

**Continue fighting the fire:**"""
            
            view = TacticalChoicesView(self.singleplayer_game, self.user_id)
            
            # Use defer + followup for clean DM conversation (no reply chains)
            if interaction.guild is None:
                await interaction.response.defer()
                await interaction.followup.send(message, view=view)
            else:
                await interaction.response.send_message(message, view=view)
    
    def _create_progression_message(self, result):
        """Create a message showing what changed from the previous action."""
        if not result.get("before_stats") or not result.get("after_stats"):
            return ""
            
        before = result["before_stats"]
        after = result["after_stats"]
        
        # Calculate changes
        size_change = after['fire_size_acres'] - before['fire_size_acres']
        containment_change = after['containment_percent'] - before['containment_percent']
        
        # Get budget change from result
        cost = result.get('cost', 0)
        
        # Get effectiveness data from the user state for strategic feedback
        user_state = self.singleplayer_game.get_user_state(self.user_id)
        effectiveness_data = user_state.get("last_effectiveness", {})
        
        # Format changes with clear +/- indicators
        changes = []
        
        # Strategic effectiveness analysis
        if effectiveness_data:
            eff_mult = effectiveness_data.get('effectiveness_multiplier', 1.0)
            conditions = effectiveness_data.get('conditions', {})
            
            if eff_mult > 1.2:
                changes.append(f"🎯 **EXCELLENT CHOICE** - {int((eff_mult-1)*100)}% effectiveness bonus!")
            elif eff_mult < 0.8:
                changes.append(f"⚠️ **POOR CONDITIONS** - {int((1-eff_mult)*100)}% effectiveness penalty")
            else:
                changes.append(f"✅ **GOOD DEPLOYMENT** - Standard effectiveness")
        
        # Fire size change
        if size_change > 0:
            changes.append(f"📈 **Fire size: +{size_change} acres** (spreading)")
        elif size_change < 0:
            changes.append(f"📉 **Fire size: {size_change} acres** (reduced)")
        else:
            changes.append(f"➡️ **Fire size: stable** (no change)")
        
        # Containment change
        if containment_change > 0:
            changes.append(f"📈 **Containment: +{containment_change}%** (improving)")
        elif containment_change < 0:
            changes.append(f"📉 **Containment: {containment_change}%** (losing ground)")
        else:
            changes.append(f"➡️ **Containment: no change**")
            
        # Budget change (always shows the cost)
        changes.append(f"💰 **Budget: -${cost:,}** (resource cost)")
        
        # Structures threatened change
        before_threats = before.get('threatened_structures', 0)
        after_threats = after.get('threatened_structures', 0)
        structures_change = after_threats - before_threats
        
        if structures_change > 0:
            changes.append(f"🏠 **Structures: +{structures_change} at risk** (fire spreading)")
        elif structures_change < 0:
            changes.append(f"🏠 **Structures: {structures_change} at risk** (threat reduced)")
        
        return f"\n⚡ **TACTICAL ANALYSIS:**\n" + "\n".join(f"   {change}" for change in changes) + "\n"


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
                "budget": 20000,  # Starting resource budget in dollars
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
        user_state["resources_deployed"] = {"hand_crews": 1, "engines": 1, "air_tankers": 0, "dozers": 0}
        user_state["budget"] = 20000  # Starting budget in dollars
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
        
        # Capture BEFORE state for comparison
        old_stats = user_state["fire_grid"].get_fire_statistics() if user_state["fire_grid"] else None
            
        # Resource costs - SPENDING dollars on resources (daily rates)
        costs = {"hand_crews": 1800, "engines": 3200, "dozers": 4600, "air_tankers": 12000}
        cost = costs.get(resource_type, 2) * count
        
        if user_state["budget"] < cost:
            return {"success": False, "reason": "insufficient_budget", "cost": cost, "budget": user_state["budget"]}
            
        if resource_type in user_state["resources_deployed"]:
            user_state["resources_deployed"][resource_type] += count
            user_state["budget"] -= cost  # SPEND points
            user_state["actions_taken"] += 1
            
            # Apply immediate suppression effect
            self._apply_immediate_suppression(user_state, resource_type, count)
            
            # Capture AFTER state for comparison
            new_stats = user_state["fire_grid"].get_fire_statistics()
            
            return {
                "success": True, 
                "cost": cost, 
                "remaining_budget": user_state["budget"],
                "auto_progression": auto_result,
                "before_stats": old_stats,
                "after_stats": new_stats
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
            user_state["resources_deployed"]["hand_crews"] * 25 +
            user_state["resources_deployed"]["engines"] * 18 + 
            user_state["resources_deployed"]["air_tankers"] * 40 +
            user_state["resources_deployed"]["dozers"] * 30
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
        """Apply strategic suppression effect based on terrain and weather conditions."""
        base_suppression = {"hand_crews": 8, "engines": 6, "air_tankers": 15, "dozers": 10}
        
        # Get current fire and weather conditions
        stats = user_state["fire_grid"].get_fire_statistics()
        fire_size = stats['fire_size_acres']
        weather = stats['weather']
        wind_speed = weather['wind_speed']
        
        # Calculate strategic effectiveness multiplier
        effectiveness = self._calculate_resource_effectiveness(
            resource_type, fire_size, wind_speed, weather
        )
        
        # Apply strategic suppression
        base_value = base_suppression.get(resource_type, 5) * count
        strategic_suppression = int(base_value * effectiveness)
        
        # Store effectiveness for feedback
        user_state["last_effectiveness"] = {
            "resource": resource_type,
            "base_suppression": base_value,
            "effectiveness_multiplier": effectiveness,
            "final_suppression": strategic_suppression,
            "conditions": {
                "fire_size": fire_size,
                "wind_speed": wind_speed,
                "weather_suitable": effectiveness > 1.0
            }
        }
        
        user_state["fire_grid"].apply_suppression(strategic_suppression)
    
    def _calculate_resource_effectiveness(self, resource_type, fire_size, wind_speed, weather):
        """Calculate resource effectiveness based on conditions."""
        effectiveness = 1.0  # Base effectiveness
        
        if resource_type == "hand_crews":
            # Hand crews: Best for small fires and steep terrain
            if fire_size <= 30:
                effectiveness *= 1.5  # +50% on small fires
            elif fire_size >= 80:
                effectiveness *= 0.7  # -30% on large fires
            # Always reliable regardless of weather
            
        elif resource_type == "air_tankers":
            # Air support: Weather dependent, great for large fires
            if wind_speed > 20:
                effectiveness *= 0.3  # Grounded in high winds
            elif wind_speed < 10:
                effectiveness *= 1.3  # +30% in calm conditions
                
            if fire_size >= 50:
                effectiveness *= 1.8  # +80% on large fires
            elif fire_size <= 20:
                effectiveness *= 0.6  # -40% on small fires (overkill)
                
        elif resource_type == "engines":
            # Engines: Consistent, good for sustained attack
            if fire_size >= 30 and fire_size <= 100:
                effectiveness *= 1.4  # +40% in sweet spot
            # Reliable in most weather conditions
            
        elif resource_type == "dozers":
            # Dozers: Prevention specialists, terrain dependent
            if fire_size <= 60:
                effectiveness *= 1.6  # +60% for containment lines
            else:
                effectiveness *= 0.8  # Less effective once fire is large
            # Weather independent
        
        return max(0.2, effectiveness)  # Minimum 20% effectiveness
        
    def advance_operational_period(self, user_id):
        """Advance to next operational period with fire progression."""
        user_state = self.get_user_state(user_id)
        
        if not user_state["fire_grid"] or user_state["game_phase"] != "active":
            return None
            
        # Apply suppression based on deployed resources
        total_suppression = (
            user_state["resources_deployed"]["hand_crews"] * 25 +
            user_state["resources_deployed"]["engines"] * 18 + 
            user_state["resources_deployed"]["air_tankers"] * 40 +
            user_state["resources_deployed"]["dozers"] * 30
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
    @brief Enhanced wildfire incident management for Discord
    @details Enhanced implementation with real-time fire simulation:
    - Functions under 60 lines
    - Single responsibility
    - Descriptive naming
    - Real-time fire simulation with FireGrid
    - Team coordination and auto-progression
    """
    
    def __init__(self):
        self.active_fires = {}
        self.player_assignments = {}
        self.report_generator = IncidentReportGenerator()
        
    def create_fire(self, channel_id):
        """Create new fire incident with full fire simulation."""
        fire_id = f"guild_fire_{channel_id}_{int(time.time())}"
        
        # Create realistic fire simulation
        weather = WeatherConditions(
            wind_speed=random.randint(5, 25),
            wind_direction=random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
            humidity=random.randint(15, 60),
            temperature=random.randint(70, 105)
        )
        
        fire_grid = FireGrid()
        fire_grid.initialize_random_fire(weather)
        
        fire_data = {
            "id": fire_id,
            "channel_id": channel_id,
            "fire_grid": fire_grid,
            "weather": weather,
            "responders": [],
            "resources_deployed": {"hand_crews": 0, "engines": 0, "air_tankers": 0, "dozers": 0},
            "created_at": datetime.now().isoformat(),
            "next_progression": datetime.now() + timedelta(seconds=45),
            "status": "active",
            "team_budget": 50,  # Shared team budget
            "incident_name": f"Guild Fire {fire_id[-4:]}"
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
        """Get current fire status with full simulation data."""
        if fire_id not in self.active_fires:
            return None
            
        fire = self.active_fires[fire_id]
        stats = fire["fire_grid"].get_fire_statistics()
        threats = fire["fire_grid"].get_threat_assessment()
        
        return {
            "id": fire_id,
            "channel_id": fire["channel_id"],
            "incident_name": fire["incident_name"],
            "fire_size_acres": stats["fire_size_acres"],
            "containment_percent": stats["containment_percent"],
            "threat_level": threats["threat_level"],
            "threatened_structures": threats["threatened_structures"],
            "responders": fire["responders"],
            "resources_deployed": fire["resources_deployed"],
            "team_budget": fire["team_budget"],
            "weather": stats["weather"],
            "status": fire["status"]
        }
    
    def deploy_team_resources(self, fire_id, player_id, resource_type, count):
        """Deploy resources to guild fire with team coordination."""
        if fire_id not in self.active_fires:
            return {"success": False, "error": "Fire not found"}
            
        fire = self.active_fires[fire_id]
        
        # Check if player is assigned to this fire
        player_assigned = any(r["id"] == player_id for r in fire["responders"])
        if not player_assigned:
            return {"success": False, "error": "Player not assigned to this incident"}
            
        # Check team budget
        resource_costs = {"hand_crews": 2, "engines": 3, "air_tankers": 5, "dozers": 4}
        cost = resource_costs.get(resource_type, 5) * count
        
        if fire["team_budget"] < cost:
            return {"success": False, "error": "Insufficient team budget", 
                   "cost": cost, "budget": fire["team_budget"]}
        
        # Deploy resources
        fire["team_budget"] -= cost
        fire["resources_deployed"][resource_type] += count
        
        # Apply immediate suppression effect
        suppression_values = {"hand_crews": 8, "engines": 6, "air_tankers": 15, "dozers": 10}
        suppression = suppression_values.get(resource_type, 5) * count
        fire["fire_grid"].apply_suppression(suppression)
        
        # Check for auto-progression trigger
        auto_progression = None
        if datetime.now() >= fire["next_progression"]:
            auto_progression = self.auto_advance_guild_fire(fire_id)
        
        return {
            "success": True,
            "cost": cost,
            "remaining_budget": fire["team_budget"],
            "suppression_applied": suppression,
            "auto_progression": auto_progression
        }
    
    def auto_advance_guild_fire(self, fire_id):
        """Automatically advance guild fire and calculate team performance."""
        if fire_id not in self.active_fires:
            return None
            
        fire = self.active_fires[fire_id]
        
        # Get stats before progression
        old_stats = fire["fire_grid"].get_fire_statistics()
        
        # Apply suppression based on deployed resources
        total_suppression = (
            fire["resources_deployed"]["hand_crews"] * 25 +
            fire["resources_deployed"]["engines"] * 18 + 
            fire["resources_deployed"]["air_tankers"] * 40 +
            fire["resources_deployed"]["dozers"] * 30
        )
        
        fire["fire_grid"].apply_suppression(total_suppression)
        fire["fire_grid"].advance_operational_period()
        
        # Get stats after progression
        new_stats = fire["fire_grid"].get_fire_statistics()
        
        # Calculate team performance and award/deduct budget
        containment_improvement = new_stats['containment_percent'] - old_stats['containment_percent']
        size_growth = new_stats['fire_size_acres'] - old_stats['fire_size_acres']
        
        # Team EARNS budget for good performance
        budget_earned = 0
        if containment_improvement > 20:
            budget_earned = 12  # Excellent team coordination
        elif containment_improvement > 10:
            budget_earned = 8   # Good team progress
        elif containment_improvement > 0:
            budget_earned = 5   # Some team progress
        else:
            budget_earned = 2   # Minimal progress
            
        # Lose budget for fire growth
        if size_growth > 30:
            budget_earned -= 4  # Fire grew significantly
        elif size_growth > 15:
            budget_earned -= 2  # Some growth
            
        fire["team_budget"] += max(budget_earned, 0)
        fire["next_progression"] = datetime.now() + timedelta(seconds=45)
        
        # Check if fire is contained or critical
        if fire["fire_grid"].is_contained():
            fire["status"] = "contained"
        elif new_stats['fire_size_acres'] >= 200:
            fire["status"] = "critical_failure"
            
        return {
            "containment_change": containment_improvement,
            "size_change": size_growth,
            "budget_earned": budget_earned,
            "new_budget": fire["team_budget"],
            "new_stats": new_stats
        }


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
        elif message.content.strip() in ["4", "4️⃣"]:
            result = self.singleplayer_game.deploy_resources(message.author.id, "dozers", 1)
            await self._send_choice_response(message.channel, "Dozer", result, message.author.id)
    
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
            
            # Create a TacticalChoicesView instance to use its progression method
            view_helper = TacticalChoicesView(self.singleplayer_game, user_id)
            progression_message = view_helper._create_progression_message(result)
            
            # Get current fire status after deployment
            user_state = self.singleplayer_game.get_user_state(user_id)
            stats = user_state["fire_grid"].get_fire_statistics()
            threats = user_state["fire_grid"].get_threat_assessment()
            
            threat_emoji = "🔴" if threats['threat_level'] in ["HIGH", "EXTREME"] else "🟡" if threats['threat_level'] == "MODERATE" else "🟢"
            
            message = f"""🚒 **{resource_name.upper()} DEPLOYED!**

{progression_message}

🔥 **CURRENT FIRE STATUS:**
• **Size:** {stats['fire_size_acres']} acres
• **Containment:** {stats['containment_percent']}%
• **Threat:** {threat_emoji} {threats['threat_level']} - {threats['threatened_structures']} structures at risk

💰 **Budget:** ${result['remaining_budget']:,} remaining
{auto_message}

**Continue fighting the fire:**"""
            
            # Create new tactical choices view
            view = TacticalChoicesView(self.singleplayer_game, user_id)
            await channel.send(message, view=view)
            
        else:
            # Game over - no more budget
            user_state = self.singleplayer_game.get_user_state(user_id)
            stats = user_state["fire_grid"].get_fire_statistics()
            
            # Set game phase to failed
            user_state["game_phase"] = "failed"
            
            message = f"""💥 **GAME OVER - OUT OF BUDGET!**

🔥 **FINAL FIRE STATUS:**
• **Size:** {stats['fire_size_acres']} acres
• **Containment:** {stats['containment_percent']}%

💰 **Budget:** ${result['budget']:,} (Need ${result['cost']:,} for {resource_name})

🎯 **RESULT:** Fire continued to spread without sufficient resources!

**Use `/start` to try again!**"""
            
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
        # Check if there's already an active fire in this channel
        for fire_id, fire_data in self.game.active_fires.items():
            if fire_data["channel_id"] == interaction.channel.id and fire_data["status"] == "active":
                await interaction.response.send_message(
                    f"❌ **{fire_data['incident_name']}** is already active in this channel!\n"
                    f"Use `/respond` to join the team or `/firestatus` to check progress.",
                    ephemeral=True
                )
                return
                
        fire_data = self.game.create_fire(interaction.channel.id)
        fire_status = self.game.get_fire_status(fire_data["id"])
        
        message = f"""🚨 **WILDFIRE INCIDENT REPORTED**

🔥 **{fire_status['incident_name'].upper()} - TEAM RESPONSE NEEDED**

📍 **INCIDENT DETAILS:**
• **Size:** {fire_status['fire_size_acres']} acres  
• **Containment:** {fire_status['containment_percent']}%
• **Threat:** {fire_status['threat_level']} - {fire_status['threatened_structures']} structures at risk
• **Weather:** {fire_status['weather']['wind_speed']} mph winds, {fire_status['weather']['humidity']}% humidity

💰 **Team Budget:** ${fire_status['team_budget']}k for coordinated response

🚒 **Team members use `/respond` to join the incident response!**
⚡ **Real-time fire progression** will begin automatically every 45 seconds!"""
        
        await interaction.response.send_message(message)
        
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
            # Use defer + followup for clean DM conversation (no reply chains)
            await interaction.response.defer()
            await interaction.followup.send(
                "🔥 **Ready for Action!**\n\nNo active wildfire incident. Use `/start` to begin your Incident Commander training!"
            )
            return
            
        # Deploy additional resources to the incident
        resource_deployed = random.choice(["hand_crews", "engines", "air_tankers", "dozers"])
        result = self.singleplayer_game.deploy_resources(interaction.user.id, resource_deployed, 1)
        
        if result["success"]:
            resource_names = {
                "hand_crews": "Hand Crew",
                "engines": "Engine Company", 
                "air_tankers": "Air Tanker",
                "dozers": "Dozer"
            }
            
            embed = discord.Embed(
                title="🚒 RESOURCES DEPLOYED",
                description=f"**{resource_names[resource_deployed]}** deployed to {user_state['incident_name']}",
                color=0x00AA00
            )
            
            embed.add_field(
                name="💰 COST",
                value=f"**-${result['cost']:,}** (Budget: ${result['remaining_budget']:,} remaining)",
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
                    f"Need ${result['cost']:,}, you have ${result['budget']:,}\n"
                    f"💡 Use `/advance` to progress and potentially get more funding",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "❌ Unable to deploy resources at this time", ephemeral=True
                )
            
    async def _handle_multiplayer_respond(self, interaction: discord.Interaction):
        """Handle response assignment in Guild (multiplayer mode)."""
        # Find active fire in this channel
        active_fire = None
        for fire_id, fire_data in self.game.active_fires.items():
            if fire_data["channel_id"] == interaction.channel.id and fire_data["status"] == "active":
                active_fire = fire_data
                break
        
        if not active_fire:
            await interaction.response.send_message(
                "❌ No active fire in this channel. Use `/fire` to create an incident.",
                ephemeral=True
            )
            return
            
        # Assign player to the fire if not already assigned
        success = self.game.assign_player(
            active_fire["id"],
            interaction.user.id, 
            interaction.user.display_name
        )
        
        if not success and interaction.user.id in self.game.player_assignments:
            # Player already assigned, allow resource deployment
            pass
        
        # Get current fire status for display
        fire_status = self.game.get_fire_status(active_fire["id"])
        if not fire_status:
            await interaction.response.send_message("❌ Fire status unavailable", ephemeral=True)
            return
            
        threat_emoji = "🔴" if fire_status['threat_level'] in ["HIGH", "EXTREME"] else "🟡" if fire_status['threat_level'] == "MODERATE" else "🟢"
        
        message = f"""🚒 **TEAM RESOURCE DEPLOYMENT**

{interaction.user.display_name} responding to **{fire_status['incident_name'].upper()}**

🔥 **CURRENT STATUS:**
• **Size:** {fire_status['fire_size_acres']} acres
• **Containment:** {fire_status['containment_percent']}%
• **Threat:** {threat_emoji} {fire_status['threat_level']} - {fire_status['threatened_structures']} structures at risk

👥 **TEAM RESOURCES DEPLOYED:**
• **Ground Crews:** {fire_status['resources_deployed']['hand_crews']} units
• **Engines:** {fire_status['resources_deployed']['engines']} units  
• **Air Support:** {fire_status['resources_deployed']['air_tankers']} units
• **Dozers:** {fire_status['resources_deployed']['dozers']} units

💰 **Team Budget:** ${fire_status['team_budget']}k remaining

**Choose your tactical deployment:**"""

        # Create team tactical choices view
        view = TeamTacticalChoicesView(self.game, active_fire["id"], interaction.user.id)
        await interaction.response.send_message(message, view=view)
            
        
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
            # Use defer + followup for clean DM conversation (no reply chains)
            await interaction.response.defer()
            await interaction.followup.send(
                "🔥 **Ready to Respond!**\n\nNo active wildfire incident to report. Use `/start` to begin your next Incident Commander scenario!"
            )
            return
            
        # Generate situation update report
        status_report = self.singleplayer_game.generate_incident_report(
            interaction.user.id, "status"
        )
        
        await interaction.response.send_message(f"```{status_report}```")
        
    async def _handle_multiplayer_status(self, interaction: discord.Interaction):
        """Handle status display in Guild (multiplayer mode)."""
        # Find active fire in this channel
        active_fire = None
        for fire_id, fire_data in self.game.active_fires.items():
            if fire_data["channel_id"] == interaction.channel.id and fire_data["status"] == "active":
                active_fire = fire_data
                break
        
        if not active_fire:
            await interaction.response.send_message(
                "📍 No active fires in this channel. Use `/fire` to create an incident.", ephemeral=True
            )
            return
            
        # Get detailed fire status
        fire_status = self.game.get_fire_status(active_fire["id"])
        if not fire_status:
            await interaction.response.send_message("❌ Fire status unavailable", ephemeral=True)
            return
            
        threat_emoji = "🔴" if fire_status['threat_level'] in ["HIGH", "EXTREME"] else "🟡" if fire_status['threat_level'] == "MODERATE" else "🟢"
        responder_names = [r["name"] for r in fire_status["responders"]]
        
        message = f"""🔥 **TEAM INCIDENT STATUS REPORT**

📋 **{fire_status['incident_name'].upper()}**

🔥 **CURRENT FIRE STATUS:**
• **Size:** {fire_status['fire_size_acres']} acres
• **Containment:** {fire_status['containment_percent']}%
• **Threat:** {threat_emoji} {fire_status['threat_level']} - {fire_status['threatened_structures']} structures at risk

🌡️ **WEATHER CONDITIONS:**
• **Wind:** {fire_status['weather']['wind_speed']} mph {fire_status['weather']['wind_direction']}
• **Humidity:** {fire_status['weather']['humidity']}%
• **Temperature:** {fire_status['weather']['temperature']}°F

👥 **TEAM COORDINATION:**
• **Responders:** {len(responder_names)} team members
• **Team:** {', '.join(responder_names) if responder_names else 'None assigned'}

🚒 **TEAM RESOURCES DEPLOYED:**
• **Ground Crews:** {fire_status['resources_deployed']['hand_crews']} units
• **Engines:** {fire_status['resources_deployed']['engines']} units
• **Air Support:** {fire_status['resources_deployed']['air_tankers']} units
• **Dozers:** {fire_status['resources_deployed']['dozers']} units

💰 **Team Budget:** ${fire_status['team_budget']}k remaining

**Team members use `/respond` to deploy additional resources!**"""
        
        await interaction.response.send_message(message)
        
        
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
        
        # Use defer + followup for clean DM conversation (no reply chains)
        await interaction.response.defer()
        await interaction.followup.send(dispatch_message, view=view)
        
    @discord.app_commands.command(name="debugplayer2", description="🧪 [DEBUG] Simulate Player 2 for multiplayer testing")
    async def debug_player2_command(self, interaction: discord.Interaction):
        """Debug command to simulate Player 2 for testing multiplayer."""
        if interaction.guild is None:
            await interaction.response.send_message("❌ Debug commands only work in guild channels", ephemeral=True)
            return
            
        # Find active fire in this channel
        active_fire = None
        for fire_id, fire_data in self.game.active_fires.items():
            if fire_data["channel_id"] == interaction.channel.id and fire_data["status"] == "active":
                active_fire = fire_data
                break
        
        if not active_fire:
            await interaction.response.send_message("❌ No active fire to join. Use `/fire` first.", ephemeral=True)
            return
            
        # Simulate Player 2 joining (fake user ID)
        fake_player2_id = interaction.user.id + 999999  # Create fake Player 2 ID
        success = self.game.assign_player(
            active_fire["id"],
            fake_player2_id,
            f"{interaction.user.display_name}-Player2"
        )
        
        if success:
            await interaction.response.send_message(
                f"🧪 **DEBUG**: Simulated **{interaction.user.display_name}-Player2** joining the team!\n"
                f"You can now test team coordination. Use `/debugp2deploy` to simulate Player 2 deployments."
            )
        else:
            await interaction.response.send_message("❌ Unable to add Player 2", ephemeral=True)
    
    @discord.app_commands.command(name="debugp2deploy", description="🧪 [DEBUG] Deploy resources as simulated Player 2")
    @discord.app_commands.describe(
        resource="Resource type to deploy as Player 2",
        count="Number of units to deploy"
    )
    @discord.app_commands.choices(resource=[
        discord.app_commands.Choice(name="Ground Crews ($2k)", value="hand_crews"),
        discord.app_commands.Choice(name="Air Support ($5k)", value="air_tankers"),
        discord.app_commands.Choice(name="Engine Company ($3k)", value="engines"),
        discord.app_commands.Choice(name="Dozer ($4k)", value="dozers")
    ])
    async def debug_p2_deploy_command(self, interaction: discord.Interaction, resource: str, count: int = 1):
        """Debug command to deploy resources as simulated Player 2."""
        if interaction.guild is None:
            await interaction.response.send_message("❌ Debug commands only work in guild channels", ephemeral=True)
            return
            
        # Find active fire in this channel
        active_fire = None
        for fire_id, fire_data in self.game.active_fires.items():
            if fire_data["channel_id"] == interaction.channel.id and fire_data["status"] == "active":
                active_fire = fire_data
                break
        
        if not active_fire:
            await interaction.response.send_message("❌ No active fire found", ephemeral=True)
            return
            
        # Deploy as fake Player 2
        fake_player2_id = interaction.user.id + 999999
        result = self.game.deploy_team_resources(active_fire["id"], fake_player2_id, resource, count)
        
        resource_names = {
            "hand_crews": "Ground Crews",
            "air_tankers": "Air Support", 
            "engines": "Engine Company",
            "dozers": "Dozer"
        }
        
        if result["success"]:
            fire_status = self.game.get_fire_status(active_fire["id"])
            message = f"""🧪 **DEBUG DEPLOYMENT - PLAYER 2**

👤 **{interaction.user.display_name}-Player2** deployed {resource_names[resource]} x{count}

🔥 **TEAM FIRE STATUS:**
• **Size:** {fire_status['fire_size_acres']} acres  
• **Containment:** {fire_status['containment_percent']}%

👥 **TEAM RESOURCES DEPLOYED:**
• **Ground Crews:** {fire_status['resources_deployed']['hand_crews']} units
• **Engines:** {fire_status['resources_deployed']['engines']} units
• **Air Support:** {fire_status['resources_deployed']['air_tankers']} units  
• **Dozers:** {fire_status['resources_deployed']['dozers']} units

💰 **Team Budget:** ${fire_status['team_budget']}k remaining

**This simulates Player 2's deployment for testing team coordination!**"""
            
            await interaction.response.send_message(message)
        else:
            await interaction.response.send_message(
                f"❌ **Player 2 deployment failed**: {result.get('error', 'Unknown error')}", ephemeral=True
            )

    @discord.app_commands.command(name="debugstatus", description="🧪 [DEBUG] Show detailed multiplayer debug info")
    async def debug_status_command(self, interaction: discord.Interaction):
        """Debug command to show detailed multiplayer state."""
        if interaction.guild is None:
            await interaction.response.send_message("❌ Debug commands only work in guild channels", ephemeral=True)
            return
            
        # Find active fire in this channel
        active_fire = None
        for fire_id, fire_data in self.game.active_fires.items():
            if fire_data["channel_id"] == interaction.channel.id and fire_data["status"] == "active":
                active_fire = fire_data
                break
        
        if not active_fire:
            await interaction.response.send_message("❌ No active fire found", ephemeral=True)
            return
            
        fire_status = self.game.get_fire_status(active_fire["id"])
        next_progression = active_fire.get("next_progression", "Not set")
        
        message = f"""🧪 **DEBUG STATUS - MULTIPLAYER FIRE**

📋 **Fire ID:** {active_fire['id']}
📍 **Channel ID:** {active_fire['channel_id']}
⏰ **Next Progression:** {next_progression}
📊 **Status:** {active_fire['status']}

👥 **Team Responders:**"""
        
        for responder in fire_status['responders']:
            message += f"\n• **{responder['name']}** (ID: {responder['id']})"
            
        message += f"""

🚒 **Resources Deployed:**
• **Ground Crews:** {fire_status['resources_deployed']['hand_crews']} units  
• **Engines:** {fire_status['resources_deployed']['engines']} units
• **Air Support:** {fire_status['resources_deployed']['air_tankers']} units
• **Dozers:** {fire_status['resources_deployed']['dozers']} units

💰 **Team Budget:** ${fire_status['team_budget']}k
🔥 **Fire Size:** {fire_status['fire_size_acres']} acres
📈 **Containment:** {fire_status['containment_percent']}%

**Auto-progression active every 45 seconds!**"""
        
        await interaction.response.send_message(message)

    @discord.app_commands.command(name="debugclear", description="🧪 [DEBUG] Clear all guild fires for testing")
    async def debug_clear_command(self, interaction: discord.Interaction):
        """Debug command to clear all guild fires for clean testing."""
        if interaction.guild is None:
            await interaction.response.send_message("❌ Debug commands only work in guild channels", ephemeral=True)
            return
            
        # Clear all active fires
        cleared_count = len(self.game.active_fires)
        self.game.active_fires.clear()
        self.game.player_assignments.clear()
        
        await interaction.response.send_message(
            f"🧪 **DEBUG**: Cleared {cleared_count} active guild fires.\n"
            f"Ready for fresh multiplayer testing! Use `/fire` to create a new incident."
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
            # Use defer + followup for clean DM conversation (no reply chains)
            await interaction.response.defer()
            await interaction.followup.send(
                "🔥 **Ready for Command!**\n\nNo active incident to advance. Use `/start` to begin a wildfire scenario!"
            )
            return
            
        # Generate operational briefing
        briefing = self.singleplayer_game.generate_incident_report(
            interaction.user.id, "briefing"
        )
        
        # Send operational briefing as readable text with tactical choices
        briefing_message = await self._create_operational_message(interaction.user.id)
        view = TacticalChoicesView(self.singleplayer_game, interaction.user.id)
        
        # Use defer + followup for clean DM conversation (no reply chains)
        await interaction.response.defer()
        await interaction.followup.send(briefing_message, view=view)
        
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
            # Use defer + followup for clean DM conversation (no reply chains)
            await interaction.response.defer()
            await interaction.followup.send(
                "🔥 **Ready for Reports!**\n\nNo active incident to report on. Use `/start` to begin your wildfire command scenario!"
            )
            return
            
        # Use defer + followup for clean DM conversation (no reply chains)
        await interaction.response.defer()
        await interaction.followup.send(f"```{report}```")
        
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

⚡ **STRATEGIC CONDITIONS:**
• **Air Ops:** {"🟢 FAVORABLE" if stats['weather']['wind_speed'] <= 15 else "🟡 MARGINAL" if stats['weather']['wind_speed'] <= 20 else "🔴 GROUNDED"} (Wind: {stats['weather']['wind_speed']} mph)
• **Fire Size:** {"🟢 SMALL" if stats['fire_size_acres'] <= 30 else "🟡 MEDIUM" if stats['fire_size_acres'] <= 60 else "🔴 LARGE"} ({stats['fire_size_acres']} acres)
• **Urgency:** {"🟢 MANAGEABLE" if stats['fire_size_acres'] <= 50 else "🟡 CRITICAL" if stats['fire_size_acres'] <= 100 else "🔴 EMERGENCY"}


💰 **Budget:** ${user_state.get('budget', 20000):,}
*Good containment earns more funding!*


**TACTICAL OPTIONS:**

🔵 **1 🚒 Ground Crews** ($1,800) - +50% on small fires ≤30 acres
🔴 **2 🚁 Air Support** ($12,000) - +80% on large fires, ⚠️ grounded if winds >20mph  
⚫ **3 🚛 Engine Company** ($3,200) - +40% on medium fires, reliable
🟢 **4 🚜 Dozer** ($4,600) - +60% for firebreaks, prevention specialist


🎯 **GOAL:** Contain fire before it reaches 200 acres!

**Click tactical buttons OR type 1, 2, 3, or 4 to deploy!**"""

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


💰 **Budget:** ${user_state.get('budget', 20000):,}


**TACTICAL OPTIONS:**
🔵 **1 🚒** ($1,800) - Fast attack
🔴 **2 🚁** ($12,000) - Heavy power 
⚫ **3 🚛** ($3,200) - Balanced
🟢 **4 🚜** ($4,600) - Firebreaks

{time_left}

🎯 **Contain before 200 acres!**"""
        
        return message
    
    async def _send_guild_fire_update(self, fire_id, auto_result):
        """Send real-time fire update to all team members in guild channel."""
        fire_data = self.game.active_fires.get(fire_id)
        if not fire_data:
            return
            
        # Get the guild channel
        channel = self.bot.get_channel(fire_data["channel_id"])
        if not channel:
            return
            
        # Get current fire status
        fire_status = self.game.get_fire_status(fire_id)
        if not fire_status:
            return
            
        # Create team update message
        containment_change = auto_result["containment_change"]
        size_change = auto_result["size_change"]
        budget_earned = auto_result["budget_earned"]
        
        # Determine update type and emoji
        if containment_change > 10:
            status_emoji = "📈"
            status_text = "**EXCELLENT TEAM COORDINATION!**"
        elif containment_change > 0:
            status_emoji = "🔥"
            status_text = "**MAKING PROGRESS**"
        else:
            status_emoji = "🚨"
            status_text = "**FIRE SPREADING - NEED MORE RESOURCES!**"
            
        # Budget feedback
        budget_message = ""
        if budget_earned > 0:
            budget_message = f"📊 **Team earned +${budget_earned}k budget!** Great coordination!"
        else:
            budget_message = "💰 **No budget earned** - fire growth detected!"
            
        threat_emoji = "🔴" if fire_status['threat_level'] in ["HIGH", "EXTREME"] else "🟡" if fire_status['threat_level'] == "MODERATE" else "🟢"
        
        update_message = f"""{status_emoji} **TEAM FIRE UPDATE - {fire_status['incident_name'].upper()}**

{status_text}

🔥 **CURRENT STATUS:**
• **Size:** {fire_status['fire_size_acres']} acres ({size_change:+.1f} acres)
• **Containment:** {fire_status['containment_percent']}% ({containment_change:+.1f}%)
• **Threat:** {threat_emoji} {fire_status['threat_level']} - {fire_status['threatened_structures']} structures at risk

👥 **TEAM RESOURCES:**
• **Ground Crews:** {fire_status['resources_deployed']['hand_crews']} units
• **Engines:** {fire_status['resources_deployed']['engines']} units  
• **Air Support:** {fire_status['resources_deployed']['air_tankers']} units
• **Dozers:** {fire_status['resources_deployed']['dozers']} units

💰 **Team Budget:** ${fire_status['team_budget']}k remaining
{budget_message}

**Team members use `/respond` to deploy more resources!**"""

        # Check for mission accomplished
        if fire_status["status"] == "contained":
            update_message = f"""🎉 **MISSION ACCOMPLISHED - FIRE CONTAINED!**

🏆 **{fire_status['incident_name'].upper()} - TEAM SUCCESS!**

✅ **FINAL STATUS:**
• **Size:** {fire_status['fire_size_acres']} acres
• **Containment:** 100% 
• **Team Budget:** ${fire_status['team_budget']}k remaining

🚒 **EXCELLENT TEAMWORK!** This fire has been successfully contained through coordinated team effort!

**Ready for your next incident? Use `/fire` to start another team response!**"""
            
        elif fire_status["status"] == "critical_failure":
            update_message = f"""💥 **CRITICAL FAILURE - FIRE OUT OF CONTROL!**

🚨 **{fire_status['incident_name'].upper()} - EVACUATION ORDERED!**

❌ **FINAL STATUS:**
• **Size:** {fire_status['fire_size_acres']} acres (OVER 200 ACRES)
• **Containment:** {fire_status['containment_percent']}%
• **Team Budget:** ${fire_status['team_budget']}k remaining

⚠️ **FIRE TOO LARGE TO CONTAIN** - Emergency evacuation protocols activated!

**Learn from this experience! Use `/fire` to try another team response.**"""
        
        try:
            await channel.send(update_message)
        except discord.Forbidden:
            print(f"Cannot send update to channel {fire_data['channel_id']} - permissions issue")
        except Exception as e:
            print(f"Error sending guild fire update: {e}")
    
    async def _auto_progression_loop(self):
        """Background task that automatically progresses fires and sends updates."""
        while True:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                # Process singleplayer fires
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
                
                # Process guild fires
                for fire_id, fire_data in list(self.game.active_fires.items()):
                    if fire_data["status"] != "active":
                        continue
                        
                    next_progression = fire_data.get("next_progression")
                    if not next_progression:
                        continue
                        
                    # Check if it's time for auto-progression
                    if datetime.now() >= next_progression:
                        try:
                            # Auto-advance the guild fire
                            auto_result = self.game.auto_advance_guild_fire(fire_id)
                            if not auto_result:
                                continue
                                
                            # Send team updates to all responders
                            await self._send_guild_fire_update(fire_id, auto_result)
                                
                        except Exception as e:
                            print(f"Error in guild fire auto-progression for {fire_id}: {e}")
                            
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