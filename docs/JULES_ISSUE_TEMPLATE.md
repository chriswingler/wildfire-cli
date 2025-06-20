# Jules Issue Quick Reference

Use this template to add context to any Jules-assigned issue:

---

## 🤖 Jules Quick Context

> **📚 ESSENTIAL**: Read [docs/JULES_CONTEXT.md](../blob/main/docs/JULES_CONTEXT.md) for complete project understanding before starting any work.

### Project Summary
**Wildfire CLI** is a text-based wildfire incident commander simulation game that teaches real firefighting tactics through Discord bot interactions.

### Key Architecture
- **Discord Bot** (`discord.py`) with async slash commands
- **Game Engine** (`fire_engine.py`) - fire simulation and reports  
- **Database** (`aiosqlite`) for game state persistence
- **Text-Only Interface** - no visual fire grid, professional reports only

### Code Patterns to Follow
```python
# Discord commands
@discord.app_commands.command()
async def command(self, interaction: discord.Interaction):
    try:
        # Game operation
        result = await self.game.operation()
        await interaction.response.send_message(result)
    except discord.Forbidden:
        # Specific error handling
    except Exception as e:
        logger.error(f"Error: {e}")

# Database operations  
async with aiosqlite.connect(self.db_path) as db:
    result = await db.execute("SELECT ...", params)
    await db.commit()
```

### What NOT to Change
- Game logic, balance, or educational content
- User interface or Discord command structure  
- Database schema (except optimization)
- Core game algorithms or fire behavior

### Testing Requirements
- All changes must preserve existing functionality
- Use pytest with pytest-asyncio for async testing
- Mock Discord interactions, use temporary databases
- Verify no regressions in game behavior

### Files Reference
- `docs/coding_standards.md` - Project coding standards
- `src/discord_wildfire.py` - Main bot (2,201 lines, needs splitting)
- `requirements.txt` - Current dependencies

### 🔄 **If Jules Gets Stuck**

**Retrigger Process**:
1. **Pause task** in Jules interface
2. **Remove/re-add label**: `gh issue edit [#] --remove-label "assign-to-jules" && sleep 3 && gh issue edit [#] --add-label "assign-to-jules"`
3. **Add specific guidance** comment with exact implementation steps
4. **Include file paths and concrete actions**

**Effective Guidance Format**:
```
Jules, please implement [SPECIFIC TASK]:
1. CREATE [exact file] with [specific content]
2. MODIFY [specific location] 
3. APPLY [specific pattern]
START NOW with Step 1.
```

---

**Copy this context block into Jules issues that need better guidance.**