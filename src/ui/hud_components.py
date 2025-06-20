"""
@file hud_components.py
@brief Consistent HUD-style UI components for Discord wildfire interface
@details Standardized embed builders and formatting for uniform user experience
"""

import discord
from typing import Dict, List, Optional, Any
from datetime import datetime
from config.settings import config


class HUDColors:
    """Standardized color palette for HUD interface."""
    
    # Main HUD colors
    PRIMARY = 0x2F3136      # Dark blue/gray for main backgrounds
    SECONDARY = 0x36393F    # Slightly lighter gray for secondary elements
    
    # Status colors
    CRITICAL = config.discord.embed_color_codes.danger     # Red - fires, emergencies, high threat
    WARNING = config.discord.embed_color_codes.warning      # Orange - moderate threats, warnings
    SUCCESS = config.discord.embed_color_codes.success      # Green - contained, success states
    INFO = config.discord.embed_color_codes.info         # Blue - general information, neutral
    
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
    """Minimal HUD component builders for clean, focused interface."""
    
    @staticmethod
    def create_fire_grid_visual(fire_grid, size: int = 6) -> str:
        """Create ASCII/emoji representation of fire grid state."""
        if not fire_grid:
            return "```\n🟫🟫🟫🟫🟫🟫\n🟫🟩🟩🟩🟩🟫\n🟫🟩🔥🔥🟩🟫\n🟫🟩🔥🔥🟩🟫\n🟫🟩🟩🟩🟩🟫\n🟫🟫🟫🟫🟫🟫\n```"
        
        try:
            # Get grid state from fire_grid
            grid_state = fire_grid.grid if hasattr(fire_grid, 'grid') else []
            
            if not grid_state or len(grid_state) == 0:
                # Default grid if no data
                return "```\n🟫🟫🟫🟫🟫🟫\n🟫🟩🟩🟩🟩🟫\n🟫🟩🔥🔥🟩🟫\n🟫🟩🔥🔥🟩🟫\n🟫🟩🟩🟩🟩🟫\n🟫🟫🟫🟫🟫🟫\n```"
            
            # Create visual representation
            grid_visual = "```\n"
            for row in grid_state[:size]:  # Limit to size x size
                row_str = ""
                for cell in row[:size]:
                    if hasattr(cell, 'state'):
                        state = cell.state
                    elif isinstance(cell, dict):
                        state = cell.get('state', 'empty')
                    else:
                        state = str(cell).lower()
                    
                    # Map cell states to emojis
                    if 'burning' in state or 'fire' in state:
                        row_str += "🔥"
                    elif 'burned' in state or 'ash' in state:
                        row_str += "🟫"
                    elif 'contained' in state or 'suppressed' in state:
                        row_str += "🚫"
                    elif 'water' in state or 'retardant' in state:
                        row_str += "🟦"
                    else:
                        row_str += "🟩"  # Unburned/vegetation
                
                grid_visual += row_str + "\n"
            grid_visual += "```"
            return grid_visual
            
        except Exception as e:
            # Fallback if grid parsing fails
            return "```\n🟫🟫🟫🟫🟫🟫\n🟫🟩🔥🔥🟩🟫\n🟫🔥🔥🔥🔥🟫\n🟫🔥🔥🔥🔥🟫\n🟫🟩🟩🟩🟩🟫\n🟫🟫🟫🟫🟫🟫\n```"
    
    @staticmethod
    def create_progress_bar(percentage: int, width: int = 20) -> str:
        """Create visual progress bar for containment."""
        filled = int(percentage / 100 * width)
        empty = width - filled
        
        if percentage >= 90:
            bar_char = "🟩"  # Green for high containment
        elif percentage >= 50:
            bar_char = "🟨"  # Yellow for medium containment  
        else:
            bar_char = "🟥"  # Red for low containment
            
        return f"{'█' * filled}{'░' * empty} {percentage}%"
    
    @staticmethod
    def create_minimal_embed(title: str, status_type: str = "info") -> discord.Embed:
        """Create minimal embed with just title and color."""
        color_map = {
            "critical": HUDColors.CRITICAL,
            "warning": HUDColors.WARNING,
            "success": HUDColors.SUCCESS,
            "info": HUDColors.INFO,
            "primary": HUDColors.PRIMARY
        }
        
        color = color_map.get(status_type, HUDColors.INFO)
        
        embed = discord.Embed(
            title=title,
            color=color,
            timestamp=datetime.now()
        )
        
        return embed

    @staticmethod
    def create_search_results_embed(query: str, results: list) -> discord.Embed:
        """Create embed for search results."""
        embed = discord.Embed(
            title="🔎 SEARCH RESULTS",
            description=f"Showing results for: `{query}`",
            color=HUDColors.INFO,
            timestamp=datetime.now()
        )
        if results:
            for i, result_text in enumerate(results):
                embed.add_field(name=f"📄 Result {i+1}", value=str(result_text)[:1020] + "..." if len(str(result_text)) > 1024 else str(result_text) , inline=False)
        else:
            embed.add_field(name="📭 NO RESULTS", value="No results found for your query.", inline=False)
        return embed

    @staticmethod
    def create_ask_response_embed(question: str, answer: str, sources: list = None, confidence: float = None) -> discord.Embed:
        """Create embed for LLM ask response."""
        embed = discord.Embed(
            title="💡 ASK RESPONSE",
            description=f"Question: `{question}`",
            color=HUDColors.PRIMARY,
            timestamp=datetime.now()
        )
        embed.add_field(name="💬 ANSWER", value=str(answer)[:1020] + "..." if len(str(answer)) > 1024 else str(answer), inline=False)
        if sources:
            source_text = "\n".join(f"- {s}" for s in sources)
            embed.add_field(name="📚 SOURCES", value=source_text, inline=False)
        if confidence is not None:
            embed.add_field(name="🎯 CONFIDENCE", value=f"{confidence:.0%}", inline=True)
        return embed

    @staticmethod
    def create_summary_embed(timeframe: str, summary_text: str, key_points: list = None, action_items: list = None, channel_name: str = None) -> discord.Embed:
        """Create embed for channel summary."""
        description = f"Summary for the last `{timeframe}`"
        if channel_name:
            description += f" in `#{channel_name}`"

        embed = discord.Embed(
            title="📋 SUMMARY",
            description=description,
            color=HUDColors.SECONDARY,
            timestamp=datetime.now()
        )
        embed.add_field(name="📝 SUMMARY", value=str(summary_text)[:1020] + "..." if len(str(summary_text)) > 1024 else str(summary_text), inline=False)
        if key_points:
            key_points_text = "\n".join(f"- {kp}" for kp in key_points)
            embed.add_field(name="🔑 KEY POINTS", value=key_points_text, inline=False)
        if action_items:
            action_items_text = "\n".join(f"- {ai}" for ai in action_items)
            embed.add_field(name="📌 ACTION ITEMS", value=action_items_text, inline=False)
        return embed
    
    @staticmethod
    def create_incident_embed(incident_name: str, fire_data: Dict[str, Any], fire_grid=None) -> discord.Embed:
        """Create minimal incident HUD with essential elements only."""
        # Determine status type
        containment = fire_data.get('containment_percent', 0)
        if containment >= 75:
            status_type = "success"
        elif containment >= 25:
            status_type = "warning"
        else:
            status_type = "critical"
        
        embed = HUDComponents.create_minimal_embed(
            f"🔥 {incident_name.upper()}",
            status_type
        )
        
        # Progress Bar (Containment)
        progress_bar = HUDComponents.create_progress_bar(containment)
        embed.add_field(
            name="📊 CONTAINMENT",
            value=f"`{progress_bar}`",
            inline=False
        )
        
        # Balance (Budget)
        budget = fire_data.get('budget', fire_data.get('team_budget', 0))
        embed.add_field(
            name="💰 BUDGET",
            value=f"`${budget:,}k`",
            inline=True
        )
        
        # Stock (Resources)
        resources = fire_data.get('resources_deployed', {})
        total_resources = sum([
            resources.get('hand_crews', 0),
            resources.get('engines', 0),
            resources.get('air_tankers', 0),
            resources.get('dozers', 0)
        ])
        embed.add_field(
            name="🚒 RESOURCES",
            value=f"`{total_resources} units`",
            inline=True
        )
        
        # Fire Grid Visual (replacing image)
        fire_visual = HUDComponents.create_fire_grid_visual(fire_grid)
        embed.add_field(
            name="🗺️ FIRE GRID",
            value=fire_visual,
            inline=False
        )
        
        return embed
    
    @staticmethod
    def create_action_embed(title: str, description: str, success: bool = True) -> discord.Embed:
        """Create standardized action result embed."""
        status_type = "success" if success else "critical"
        
        embed = HUDComponents.create_status_embed(title, description, status_type)
        
        return embed
    
    @staticmethod
    def create_resource_deployment_embed(resource_name: str, deployment_result: Dict[str, Any], fire_status: Dict[str, Any], fire_grid=None) -> discord.Embed:
        """Create minimal resource deployment result embed."""
        success = deployment_result.get('success', False)
        status_type = "success" if success else "critical"
        
        embed = HUDComponents.create_minimal_embed(
            f"🚒 {resource_name.upper()} DEPLOYED",
            status_type
        )
        
        # Progress Bar (Updated Containment)
        containment = fire_status.get('containment_percent', 0)
        progress_bar = HUDComponents.create_progress_bar(containment)
        embed.add_field(
            name="📊 CONTAINMENT",
            value=f"`{progress_bar}`",
            inline=False
        )
        
        # Budget and Resources side by side
        budget = fire_status.get('budget', fire_status.get('team_budget', 0))
        embed.add_field(
            name="💰 BUDGET",
            value=f"`${budget:,}k`",
            inline=True
        )
        
        resources = fire_status.get('resources_deployed', {})
        total_resources = sum([
            resources.get('hand_crews', 0),
            resources.get('engines', 0),
            resources.get('air_tankers', 0),
            resources.get('dozers', 0)
        ])
        embed.add_field(
            name="🚒 RESOURCES",
            value=f"`{total_resources} units`",
            inline=True
        )
        
        # Fire Grid Visual
        fire_visual = HUDComponents.create_fire_grid_visual(fire_grid)
        embed.add_field(
            name="🗺️ FIRE GRID",
            value=fire_visual,
            inline=False
        )
        
        return embed
    
    @staticmethod
    def create_team_deployment_embed(user_name: str, resource_name: str, fire_status: Dict[str, Any], fire_grid=None, auto_progression: Optional[Dict[str, Any]] = None) -> discord.Embed:
        """Create minimal team deployment embed."""
        containment = fire_status.get('containment_percent', 0)
        status_type = "success" if containment >= 75 else "warning" if containment >= 25 else "critical"
        
        embed = HUDComponents.create_minimal_embed(
            f"👥 TEAM: {resource_name.upper()}",
            status_type
        )
        
        # Who deployed
        embed.add_field(
            name="👤 DEPLOYED BY",
            value=f"`{user_name}`",
            inline=False
        )
        
        # Progress Bar (Containment)
        progress_bar = HUDComponents.create_progress_bar(containment)
        embed.add_field(
            name="📊 CONTAINMENT",
            value=f"`{progress_bar}`",
            inline=False
        )
        
        # Budget and Resources side by side
        budget = fire_status.get('team_budget', fire_status.get('budget', 0))
        embed.add_field(
            name="💰 TEAM BUDGET",
            value=f"`${budget:,}k`",
            inline=True
        )
        
        resources = fire_status.get('resources_deployed', {})
        total_resources = sum([
            resources.get('hand_crews', 0),
            resources.get('engines', 0),
            resources.get('air_tankers', 0),
            resources.get('dozers', 0)
        ])
        embed.add_field(
            name="🚒 TEAM RESOURCES",
            value=f"`{total_resources} units`",
            inline=True
        )
        
        # Fire Grid Visual
        fire_visual = HUDComponents.create_fire_grid_visual(fire_grid)
        embed.add_field(
            name="🗺️ FIRE GRID",
            value=fire_visual,
            inline=False
        )
        
        # Auto progression bonus message
        if auto_progression and auto_progression.get('budget_earned', 0) > 0:
            embed.add_field(
                name="🏆 TEAM BONUS",
                value=f"`+${auto_progression['budget_earned']}k budget!`",
                inline=False
            )
        
        return embed
    
    @staticmethod
    def create_simple_info_embed(title: str, description: str, fields: Optional[List[Dict[str, Any]]] = None) -> discord.Embed:
        """Create minimal informational embed."""
        embed = HUDComponents.create_minimal_embed(title, "info")
        
        if description:
            embed.add_field(
                name="ℹ️ INFO",
                value=f"`{description}`",
                inline=False
            )
        
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
        """Create minimal error embed."""
        embed = HUDComponents.create_minimal_embed(title, "critical")
        
        embed.add_field(
            name="❌ ERROR",
            value=f"`{description}`",
            inline=False
        )
        
        if suggestions:
            suggestion_text = "\n".join(f"`{suggestion}`" for suggestion in suggestions)
            embed.add_field(
                name="💡 SUGGESTIONS",
                value=suggestion_text,
                inline=False
            )
        
        return embed
    
    @staticmethod
    def create_action_embed(title: str, description: str, success: bool = True) -> discord.Embed:
        """Create minimal action result embed."""
        status_type = "success" if success else "critical"
        embed = HUDComponents.create_minimal_embed(title, status_type)
        
        icon = "✅" if success else "❌"
        embed.add_field(
            name=f"{icon} RESULT",
            value=f"`{description}`",
            inline=False
        )
        
        return embed