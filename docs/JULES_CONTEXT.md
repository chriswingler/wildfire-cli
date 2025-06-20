# Jules Autonomous Coding Agent - Project Context

This document provides comprehensive context for Jules when working on Wildfire CLI tasks.

## 📋 Project Overview

**Wildfire CLI** is a text-based wildfire incident commander simulation game that teaches real-world firefighting tactics using authentic Incident Command System (ICS) protocols.

### Core Purpose
- **Educational**: Teach firefighting tactics and ICS protocols
- **Realistic**: Uses authentic wildfire terminology and procedures  
- **Text-Based**: Professional terminal interface, NO visual fire representations
- **Discord Integration**: Multiplayer coordination through Discord bot

### Key Design Principles
- **No Visual Fire Grid**: Fire data stays internal, communicated via professional reports only
- **Authentic ICS**: Follows real Incident Command System operational periods
- **Text-Only Interface**: Uses Rich library for colors/formatting, no ASCII art
- **Educational Focus**: Teaches real emergency management principles

## 🏗️ Architecture Overview

### Core Components

#### 1. Fire Simulation Engine (`src/fire_engine.py`)
- **Purpose**: Internal fire behavior simulation using cellular automata
- **Key Functions**: Report generation, weather simulation, terrain modeling
- **IMPORTANT**: Fire grid data NEVER exposed to users - only professional reports

#### 2. Discord Bot Interface (`src/discord_wildfire.py`)
- **Purpose**: Discord command handling and user interaction
- **Features**: Singleplayer DM mode, multiplayer guild coordination
- **WARNING**: This file is 2,201 lines and violates size standards (needs splitting)

#### 3. Game Logic (`src/commands.py`, `src/commands_simple.py`)
- **Purpose**: Core game mechanics and database operations
- **Issue**: Contains duplicate logic that should be consolidated

#### 4. Report Generation (`src/incident_reports.py`)
- **Purpose**: Professional ICS-style incident reports
- **Style**: Radio communication style, authentic terminology

#### 5. UI Components (`src/ui/hud_components.py`)
- **Purpose**: Consistent colors, emojis, formatting
- **Usage**: Always use HUDColors, HUDEmojis for consistency

### File Structure
```
src/
├── discord_wildfire.py      # Main Discord bot (2,201 lines - TOO LARGE)
├── commands.py              # Game logic with database
├── commands_simple.py       # Simplified game logic
├── fire_engine.py          # Fire simulation & reports
├── incident_reports.py     # Report generation
├── utilities.py            # Helper functions
├── main.py                 # Bot startup
└── ui/
    └── hud_components.py   # UI constants & helpers
```

## 📚 Dependencies & Libraries

### Current Dependencies (`requirements.txt`)
```
discord.py>=2.3.2          # Discord bot framework
python-dotenv>=1.0.0        # Environment variables
aiosqlite>=0.17.0          # Async SQLite database
aiohttp>=3.8.0             # HTTP client
```

### Coding Patterns to Follow

#### 1. Async/Await Pattern
```python
# All Discord commands and database operations use async/await
@discord.app_commands.command()
async def command_name(self, interaction: discord.Interaction):
    async with aiosqlite.connect(self.db_path) as db:
        result = await db.execute("SELECT * FROM fires")
        await interaction.response.send_message("Response")
```

#### 2. Discord UI Components  
```python
# Use Discord UI for user interactions
class GameView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)  # Always set timeout
    
    @discord.ui.button(label='Option', style=discord.ButtonStyle.primary)
    async def button_callback(self, interaction, button):
        # Handle button interaction
```

#### 3. Database Operations
```python
# Always use aiosqlite with context managers
async def database_operation(self):
    async with aiosqlite.connect(self.db_path) as db:
        await db.execute("INSERT INTO table ...")
        await db.commit()
```

#### 4. Error Handling
```python
# Use specific exceptions, never bare except:
try:
    await some_operation()
except discord.Forbidden:
    # Handle Discord permission error
except aiosqlite.Error as e:
    # Handle database error
    logger.error(f"Database error: {e}")
```

## 🎯 Coding Standards Reference

### Function Size Limits
- **Ideal**: 4 lines
- **Maximum**: 60 lines
- **Current Violations**: 22 functions exceed limit (see issues #97-99)

### File Size Limits  
- **Maximum**: 1000 lines
- **Critical Violation**: discord_wildfire.py (2,201 lines) needs immediate splitting

### Naming Conventions
- Use descriptive, unambiguous names
- Replace magic numbers with named constants
- Example: `BUTTON_TIMEOUT_SECONDS = 300` instead of hardcoded `300`

### Documentation Style
```python
def function_name(param1: type, param2: type) -> return_type:
    """
    Brief description of function purpose.
    
    Args:
        param1: Description of parameter
        param2: Description of parameter
        
    Returns:
        Description of return value
    """
```

## 🧪 Testing Approach

### Current State
- **Minimal Testing**: Only `src/test_review.py` exists (for standards testing)
- **Need**: Comprehensive pytest-based testing following FIRST principles

### Testing Framework to Use
```python
# Use pytest with async support
import pytest
import pytest.asyncio

@pytest.mark.asyncio
async def test_async_function():
    # Test async functions
    result = await some_async_function()
    assert result == expected_value
```

### Test Structure to Follow
```
tests/
├── unit/
│   ├── test_fire_engine.py
│   ├── test_commands.py
│   └── test_utilities.py
├── integration/
│   ├── test_discord_integration.py
│   └── test_database_integration.py
└── fixtures/
    └── test_data.py
```

## 🚨 Critical Areas Needing Work

### 1. File Size Violations (URGENT)
- `discord_wildfire.py`: 2,201 lines (Issue #96)
- Must be split into logical modules

### 2. Function Size Violations  
- 22 functions exceed 60-line limit (Issues #97-99)
- Largest: `_handle_choice_result` at 277 lines

### 3. Error Handling Issues
- Bare `except:` clauses at lines 129, 1254, 1399, 1506 in discord_wildfire.py
- Need specific exception handling (Issue #104)

### 4. Configuration Management
- Hardcoded values throughout codebase (Issue #105)
- Resource costs, timeouts, thresholds need centralization

### 5. Testing Foundation
- Need pytest infrastructure (Issue #100)
- Need systematic test coverage (Issues #101-103)

## ✅ What Jules SHOULD Do

### 1. Code Refactoring
- Split large files into logical modules
- Break down oversized functions
- Eliminate code duplication
- Improve error handling

### 2. Testing Implementation
- Set up pytest infrastructure
- Create unit tests for pure functions
- Add integration tests for database operations
- Follow FIRST testing principles

### 3. Infrastructure Improvements
- Add performance monitoring
- Implement configuration management
- Set up CI/CD pipelines
- Database optimization

### 4. Code Quality
- Fix coding standards violations
- Add proper documentation
- Implement proper logging
- Remove debug code from production

## ❌ What Jules Should NOT Change

### 1. Game Logic & Balance
- Fire behavior algorithms
- Resource effectiveness calculations
- Game difficulty and balance
- Educational content accuracy

### 2. User Experience
- Discord command interface design
- Message formatting and style
- Game flow and progression
- ICS authenticity

### 3. Core Architecture Decisions
- Text-only interface principle
- No visual fire grid policy
- Discord integration approach
- Database schema structure (except optimization)

## 🔍 Common Patterns to Follow

### 1. Discord Command Structure
```python
@discord.app_commands.command(name="command", description="Description")
async def command_function(self, interaction: discord.Interaction):
    """Command implementation following patterns."""
    try:
        # Validate permissions/game state
        if not self.validate_user_state(interaction.user.id):
            await interaction.response.send_message("Error message", ephemeral=True)
            return
            
        # Perform game operation
        result = await self.perform_game_action()
        
        # Create response
        embed = discord.Embed(title="Title", description="Content")
        view = GameView() if interactive else None
        
        await interaction.response.send_message(embed=embed, view=view)
        
    except SpecificException as e:
        logger.error(f"Error in command: {e}")
        await interaction.response.send_message("User-friendly error", ephemeral=True)
```

### 2. Database Operation Pattern
```python
async def database_operation(self, param1, param2):
    """Database operation following project patterns."""
    async with aiosqlite.connect(self.db_path) as db:
        try:
            result = await db.execute(
                "SELECT * FROM table WHERE condition = ?", 
                (param1,)
            )
            data = await result.fetchall()
            await db.commit()
            return data
        except aiosqlite.Error as e:
            logger.error(f"Database error: {e}")
            raise
```

### 3. UI Component Pattern
```python
# Always use HUD components for consistency
from ui.hud_components import HUDComponents, HUDColors, HUDEmojis

embed = discord.Embed(
    title=f"{HUDEmojis.FIRE} Fire Status",
    description="Status information",
    color=HUDColors.WARNING
)
```

## 📝 Issue References

When working on Jules issues, always reference the appropriate issue numbers and follow the Definition of Done criteria. Key Jules issues:

- **#96**: Split discord_wildfire.py (CRITICAL)
- **#97-99**: Function size refactoring
- **#100-103**: Testing infrastructure  
- **#104**: Error handling improvements
- **#105**: Configuration management
- **#106**: Debug command system
- **#107**: Database optimization

## 🤖 Jules-Specific Notes

### Context Limitations
- Jules sees specific issue descriptions and accessed files
- Jules does NOT have full project context automatically
- Always include relevant context in issue descriptions
- Reference this document for comprehensive project understanding

### Best Practices for Jules
1. **Read this document first** before starting any task
2. **Follow existing code patterns** rather than introducing new approaches
3. **Test changes thoroughly** to ensure no functionality breaks
4. **Ask for clarification** if project context is unclear
5. **Reference coding standards** at `docs/coding_standards.md`

### Communication with Jules
- Provide specific, actionable tasks
- Include file paths and line numbers
- Reference existing patterns to follow
- Specify what NOT to change
- Include testing requirements

## 🔄 **Jules Task Management & Retriggering**

### When Jules Gets Stuck or Needs More Direction

**Common Scenario**: Jules says "waiting for your input" or asks for more specific direction.

### Proven Retrigger Process

**Step 1: Pause Task (Jules Interface)**
- Go to Jules web interface
- Pause/stop the current task if it's running

**Step 2: Label Toggle (GitHub CLI)**
```bash
# Remove Jules assignment
gh issue edit [ISSUE_NUMBER] --remove-label "assign-to-jules"

# Wait a moment (important for system refresh)
sleep 3

# Re-add Jules assignment  
gh issue edit [ISSUE_NUMBER] --add-label "assign-to-jules"
```

**Step 3: Add Specific Guidance**
```bash
gh issue comment [ISSUE_NUMBER] --body "**🔄 RETRIGGER REQUEST**

Jules, please implement [SPECIFIC TASK]:

1. **CREATE** [specific file/change]
2. **MODIFY** [specific location] 
3. **APPLY** [specific pattern]

**START NOW** with Step 1 - [immediate action].

This is a [priority] task for [purpose]."
```

**Step 4: Update Issue Body (Optional)**
```bash
gh issue edit [ISSUE_NUMBER] --body "$(gh issue view [ISSUE_NUMBER] --json body | jq -r '.body')

---
## 🚀 **IMMEDIATE ACTION REQUIRED**
**Jules**: Please implement the [task] outlined in the comments below.
**Priority**: [High/Medium] - [specific need]."
```

### Example Retrigger Commands

**For Performance Monitoring Issue (#75)**:
```bash
# Remove and re-add label
gh issue edit 75 --remove-label "assign-to-jules"
sleep 3
gh issue edit 75 --add-label "assign-to-jules"

# Add specific guidance
gh issue comment 75 --body "Jules, implement performance monitoring:
1. CREATE src/utils/performance.py with @time_command decorator
2. ADD psutil>=5.9.0 to requirements.txt
3. APPLY decorator to Discord commands in discord_wildfire.py
START NOW with Step 1."
```

### What Makes Retriggers Successful

**✅ Effective Triggers**:
- **Label removal/re-addition** - Forces system refresh
- **Specific implementation steps** - Clear actionable tasks
- **File paths and line numbers** - Concrete locations to work
- **Example code** - Shows exact implementation patterns
- **Priority indicators** - Signals urgency and importance

**❌ Ineffective Approaches**:
- Vague "please continue" requests
- No specific next steps
- Missing file locations
- Unclear implementation requirements

### Retrigger Timing

**When to Retrigger**:
- Jules asks "waiting for your input" 
- Jules requests "more specific task"
- Jules seems stuck on broad requirements
- Task has been idle for >30 minutes
- Need to redirect Jules to different aspect

**Retrigger Frequency**:
- Wait at least 5-10 minutes between retrigger attempts
- Don't retrigger more than 3 times per hour
- If multiple retriggers fail, issue may need human decomposition

### Success Indicators

**Jules Successfully Retriggered When**:
- Starts creating/modifying specific files
- Follows the exact implementation steps provided
- Shows progress within 10-15 minutes
- Asks clarifying questions about implementation details (not broad direction)

---

*This document should be referenced in all Jules issue descriptions to provide necessary project context.*