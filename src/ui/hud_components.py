"""
@file hud_components.py
@brief Consistent HUD-style UI components for Discord wildfire interface
@details Standardized embed builders and formatting for uniform user experience
"""

import discord
from typing import Dict, List, Optional, Any
from datetime import datetime


class HUDColors:
    """Standardized color palette for HUD interface."""
    
    # Main HUD colors
    PRIMARY = 0x2F3136      # Dark blue/gray for main backgrounds
    SECONDARY = 0x36393F    # Slightly lighter gray for secondary elements
    
    # Status colors
    CRITICAL = 0xFF4444     # Red - fires, emergencies, high threat
    WARNING = 0xFFAA00      # Orange - moderate threats, warnings
    SUCCESS = 0x44FF44      # Green - contained, success states
    INFO = 0x4488FF         # Blue - general information, neutral
    
    # Accent colors
    ACCENT = 0xFF6B35       # Orange - key highlights, interactive elements
    MUTED = 0x72767D        # Gray - secondary text, less important info


class HUDEmojis:
    """Standardized emoji set for HUD interface."""
    
    # Status indicators
    CRITICAL = "🔴"
    WARNING = "🟡"
    SUCCESS = "🟢"
    INFO = "🔵"
    
    # Fire related
    FIRE = "🔥"
    CONTAINED = "🚫"
    SPREADING = "📈"
    SHRINKING = "📉"
    
    # Resources
    CREW = "🚒"
    AIR = "🚁"
    ENGINE = "🚛"
    DOZER = "🚜"
    
    # System
    COMMAND = "📡"
    STATUS = "📊"
    ACTION = "⚡"
    BUDGET = "💰"
    
    # UI Elements
    ARROW_RIGHT = "▶️"
    ARROW_UP = "⬆️"
    ARROW_DOWN = "⬇️"
    BULLET = "•"


class HUDComponents:
    """Standardized HUD component builders for consistent interface."""
    
    @staticmethod
    def create_status_embed(title: str, description: str, status_type: str = "info") -> discord.Embed:
        """Create a standardized status embed with HUD styling."""
        color_map = {
            "critical": HUDColors.CRITICAL,
            "warning": HUDColors.WARNING,
            "success": HUDColors.SUCCESS,
            "info": HUDColors.INFO,
            "primary": HUDColors.PRIMARY
        }
        
        emoji_map = {
            "critical": HUDEmojis.CRITICAL,
            "warning": HUDEmojis.WARNING,
            "success": HUDEmojis.SUCCESS,
            "info": HUDEmojis.INFO,
            "primary": HUDEmojis.COMMAND
        }
        
        color = color_map.get(status_type, HUDColors.INFO)
        emoji = emoji_map.get(status_type, HUDEmojis.INFO)
        
        embed = discord.Embed(
            title=f"{emoji} 【SYSTEM】{title.upper()}",
            description=description,
            color=color,
            timestamp=datetime.now()
        )
        
        return embed
    
    @staticmethod
    def create_incident_embed(incident_name: str, fire_data: Dict[str, Any]) -> discord.Embed:
        """Create standardized incident status embed."""
        # Determine threat level styling
        threat_level = fire_data.get('threat_level', 'MODERATE').upper()
        if threat_level in ['HIGH', 'EXTREME']:
            status_type = "critical"
            threat_emoji = HUDEmojis.CRITICAL
        elif threat_level == 'MODERATE':
            status_type = "warning"
            threat_emoji = HUDEmojis.WARNING
        else:
            status_type = "success"
            threat_emoji = HUDEmojis.SUCCESS
        
        embed = HUDComponents.create_status_embed(
            f"INCIDENT: {incident_name}",
            f"Active wildfire requiring immediate tactical response",
            status_type
        )
        
        # Fire status section
        embed.add_field(
            name=f"{HUDEmojis.FIRE} ║ FIRE STATUS",
            value=f"```\n"
                  f"Size:        {fire_data.get('fire_size_acres', 0):>6} acres\n"
                  f"Containment: {fire_data.get('containment_percent', 0):>6}%\n"
                  f"Threat:      {threat_emoji} {threat_level}\n"
                  f"Structures:  {fire_data.get('threatened_structures', 0):>6} at risk\n"
                  f"```",
            inline=True
        )
        
        # Resource deployment section
        resources = fire_data.get('resources_deployed', {})
        embed.add_field(
            name=f"{HUDEmojis.COMMAND} ║ DEPLOYED RESOURCES",
            value=f"```\n"
                  f"Ground Crews: {resources.get('hand_crews', 0):>2} units\n"
                  f"Engines:      {resources.get('engines', 0):>2} units\n"
                  f"Air Support:  {resources.get('air_tankers', 0):>2} units\n"
                  f"Dozers:       {resources.get('dozers', 0):>2} units\n"
                  f"```",
            inline=True
        )
        
        # Command section
        budget = fire_data.get('budget', fire_data.get('team_budget', 0))
        embed.add_field(
            name=f"{HUDEmojis.STATUS} ║ COMMAND STATUS",
            value=f"```\n"
                  f"Budget:   ${budget:>8}k\n"
                  f"Period:   {fire_data.get('operational_period', 1):>8}\n"
                  f"Phase:    {fire_data.get('game_phase', 'ACTIVE').upper():>8}\n"
                  f"```",
            inline=False
        )
        
        embed.set_footer(text="ICS • Wildfire Command HUD • Real-time Tactical Display")
        
        return embed
    
    @staticmethod
    def create_action_embed(title: str, description: str, success: bool = True) -> discord.Embed:
        """Create standardized action result embed."""
        status_type = "success" if success else "critical"
        
        embed = HUDComponents.create_status_embed(title, description, status_type)
        
        return embed
    
    @staticmethod
    def create_resource_deployment_embed(resource_name: str, deployment_result: Dict[str, Any], fire_status: Dict[str, Any]) -> discord.Embed:
        """Create standardized resource deployment result embed."""
        embed = HUDComponents.create_action_embed(
            f"{resource_name.upper()} DEPLOYED",
            f"Tactical resource deployment to {fire_status.get('incident_name', 'ACTIVE INCIDENT')}",
            deployment_result.get('success', False)
        )
        
        # Add tactical analysis if available
        if 'changes' in deployment_result:
            changes = deployment_result['changes']
            embed.add_field(
                name=f"{HUDEmojis.ACTION} ║ TACTICAL ANALYSIS",
                value=changes,
                inline=False
            )
        
        # Add current status
        embed.add_field(
            name=f"{HUDEmojis.STATUS} ║ UPDATED STATUS",
            value=f"```\n"
                  f"Fire Size:    {fire_status.get('fire_size_acres', 0):>6} acres\n"
                  f"Containment:  {fire_status.get('containment_percent', 0):>6}%\n"
                  f"Budget:       ${fire_status.get('budget', fire_status.get('team_budget', 0)):>6}k\n"
                  f"```",
            inline=True
        )
        
        # Add next actions
        embed.add_field(
            name=f"{HUDEmojis.ARROW_RIGHT} ║ NEXT ACTIONS",
            value=f"{HUDEmojis.BULLET} `/respond` - Deploy additional resources\n"
                  f"{HUDEmojis.BULLET} `/firestatus` - Get situation report\n"
                  f"{HUDEmojis.BULLET} `/advance` - Progress operational period",
            inline=True
        )
        
        return embed
    
    @staticmethod
    def create_team_deployment_embed(user_name: str, resource_name: str, fire_status: Dict[str, Any], auto_progression: Optional[Dict[str, Any]] = None) -> discord.Embed:
        """Create standardized team deployment embed."""
        embed = HUDComponents.create_action_embed(
            f"TEAM DEPLOYMENT: {resource_name.upper()}",
            f"**{user_name}** deployed {resource_name} to **{fire_status.get('incident_name', 'TEAM INCIDENT')}**"
        )
        
        # Team fire status
        threat_level = fire_status.get('threat_level', 'MODERATE')
        if threat_level in ['HIGH', 'EXTREME']:
            threat_emoji = HUDEmojis.CRITICAL
        elif threat_level == 'MODERATE':
            threat_emoji = HUDEmojis.WARNING
        else:
            threat_emoji = HUDEmojis.SUCCESS
            
        embed.add_field(
            name=f"{HUDEmojis.FIRE} ║ TEAM FIRE STATUS",
            value=f"```\n"
                  f"Size:        {fire_status.get('fire_size_acres', 0):>6} acres\n"
                  f"Containment: {fire_status.get('containment_percent', 0):>6}%\n"
                  f"Threat:      {threat_emoji} {threat_level}\n"
                  f"Structures:  {fire_status.get('threatened_structures', 0):>6} at risk\n"
                  f"```",
            inline=True
        )
        
        # Team resources
        resources = fire_status.get('resources_deployed', {})
        embed.add_field(
            name=f"{HUDEmojis.COMMAND} ║ TEAM RESOURCES",
            value=f"```\n"
                  f"Ground Crews: {resources.get('hand_crews', 0):>2} units\n"
                  f"Engines:      {resources.get('engines', 0):>2} units\n"
                  f"Air Support:  {resources.get('air_tankers', 0):>2} units\n"
                  f"Dozers:       {resources.get('dozers', 0):>2} units\n"
                  f"```",
            inline=True
        )
        
        # Auto progression message
        auto_message = ""
        if auto_progression:
            if auto_progression.get('budget_earned', 0) > 0:
                auto_message = f"\n{HUDEmojis.SUCCESS} **TEAM BONUS: +${auto_progression['budget_earned']}k budget!**\nExcellent team coordination!"
            else:
                auto_message = f"\n{HUDEmojis.WARNING} **FIRE SPREADING!**\nTeam needs more suppression - deploy fast!"
        
        embed.add_field(
            name=f"{HUDEmojis.BUDGET} ║ TEAM COMMAND",
            value=f"```\nTeam Budget: ${fire_status.get('team_budget', 0):>6}k remaining```{auto_message}\n\n"
                  f"**Team members continue using `/respond` to deploy more resources!**",
            inline=False
        )
        
        return embed
    
    @staticmethod
    def create_simple_info_embed(title: str, description: str, fields: Optional[List[Dict[str, Any]]] = None) -> discord.Embed:
        """Create simple informational embed with HUD styling."""
        embed = HUDComponents.create_status_embed(title, description, "info")
        
        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get('name', 'Field'),
                    value=field.get('value', 'Value'),
                    inline=field.get('inline', False)
                )
        
        return embed
    
    @staticmethod
    def create_error_embed(title: str, description: str, suggestions: Optional[List[str]] = None) -> discord.Embed:
        """Create standardized error embed."""
        embed = HUDComponents.create_status_embed(title, description, "critical")
        
        if suggestions:
            suggestion_text = "\n".join(f"{HUDEmojis.BULLET} {suggestion}" for suggestion in suggestions)
            embed.add_field(
                name=f"{HUDEmojis.INFO} ║ SUGGESTED ACTIONS",
                value=suggestion_text,
                inline=False
            )
        
        return embed