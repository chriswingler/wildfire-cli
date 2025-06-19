"""
@mainpage Wildfire Discord MMORPG Bot
@section main_section Main Bot Entry Point

This module handles the wildfire Discord game bot initialization and startup.
Core functionality: Discord-based wildfire incident simulation and management.
"""

from discord.ext import commands
import discord
from dotenv import load_dotenv
import asyncio
import os
import logging
from commands import setup

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


async def main():
    """! 
    @brief Main asynchronous entry point for the bot
    @details Handles:
    - Cog setup initialization
    - Bot startup with environment token
    - Event loop management
    """
    await setup(bot)
    await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())
