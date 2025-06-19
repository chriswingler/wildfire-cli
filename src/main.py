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
from discord_wildfire import setup_wildfire_commands
from aiohttp import web

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


async def health_check(request):
    """Health check endpoint for DigitalOcean."""
    return web.Response(text="Wildfire bot is healthy", status=200)

async def start_health_server():
    """Start simple HTTP server for health checks."""
    app = web.Application()
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    logging.info("Health check server started on port 8080")

async def main():
    """! 
    @brief Main asynchronous entry point for the bot
    @details Handles:
    - Cog setup initialization
    - Bot startup with environment token
    - Health check server for DigitalOcean
    - Event loop management
    """
    # Setup Discord bot with Sprint 2 singleplayer mode
    await setup_wildfire_commands(bot)
    
    # Start both health server and Discord bot concurrently
    await asyncio.gather(
        start_health_server(),
        bot.start(os.getenv("DISCORD_TOKEN"))
    )

if __name__ == "__main__":
    asyncio.run(main())
