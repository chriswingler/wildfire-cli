"""
@file blazebot_integration_patch.py  
@brief Integration patch to add wildfire game to existing BlazeBot
@details Simple modification following KISS principles
"""

# ADD TO THE END OF commands.py setup() function:

"""
# Add this import at the top of commands.py:
from discord_wildfire import setup_wildfire_commands

# Add this line at the end of the setup() function in commands.py:
await setup_wildfire_commands(bot)
"""

# COMPLETE UPDATED setup() function for commands.py:
updated_setup_function = '''
async def setup(bot):
    """!
    @brief Bot setup function with wildfire game integration
    @param bot Bot instance to configure
    @details Initializes components and adds all cogs to bot
    """
    from utilities import FAQSystem, PersistentRAG, CooldownManager
    from discord_wildfire import setup_wildfire_commands
    
    faq_system = FAQSystem()
    rag = PersistentRAG()
    cooldown = CooldownManager()
    
    await bot.add_cog(WildfireCommands(bot, faq_system, rag, cooldown))
    await setup_wildfire_commands(bot)
'''

print("Integration patch ready!")
print("\nInstructions:")
print("1. Copy discord_wildfire.py to your BlazeBot directory")
print("2. Add import: from discord_wildfire import setup_wildfire_commands")
print("3. Add line to setup(): await setup_wildfire_commands(bot)")
print("4. Restart BlazeBot")
print("5. Use /fire, /respond, /firestatus commands in Discord!")