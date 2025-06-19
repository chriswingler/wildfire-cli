# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Wildfire CLI is a text-based wildfire incident commander simulation game that teaches real-world firefighting tactics and decision-making using authentic Incident Command System (ICS) protocols.

## Key Design Principles

### No Visual Fire Grid
- **Critical**: The game uses internal grid simulation but NEVER displays it visually
- All fire information is communicated through realistic incident reports only
- Fire data is converted from internal cellular automata to professional text reports
- Players receive radio-style reports about fire conditions and resource status

### Authentic Incident Command
- Game follows real ICS operational period structure (12-24 hour cycles)
- Uses authentic wildfire terminology and radio communication style
- Decisions based on real firefighting tactics and resource deployment
- Educational content teaches actual emergency management principles

### Text-Only Interface
- Professional terminal UI using Rich library for colors and formatting
- No ASCII art or visual representations of the fire
- Focus on decision-making through text-based situation reports
- Multiple choice tactical decisions with realistic consequences

## Project Structure

```
wildfire-cli/
├── src/
│   ├── discord_wildfire.py   # Discord bot with context-aware commands
│   ├── game/                 # Core game logic and simulation
│   ├── ui/                   # Rich library interface components  
│   └── scenarios/            # Game content and decision trees
├── data/                     # Scenario configurations (JSON)
├── tests/                    # Unit and integration tests
├── docs/                     # Project documentation
├── .do/                      # DigitalOcean deployment configuration
└── .github/                  # GitHub automation and templates
```

## Development Workflow

### Agile Process
- **Sprints**: 2-week cycles with 10-13 story points capacity
- **Planning**: Use GitHub Projects with custom fields for story points, epics, priorities
- **Reviews**: Focus on educational value and authentic ICS protocols
- **Testing**: >90% code coverage required, emphasis on fire simulation accuracy

### Issue Management
- Use provided issue templates for user stories, bugs, epics
- All features must include acceptance criteria and story point estimates
- Tag issues with appropriate epic labels (🔥 Fire Engine, 🎮 Game Loop, etc.)
- Follow Definition of Done checklist for all work

### Code Quality Standards
- Follow coding standards in `docs/coding_standards.md`
- Keep functions small (max 60 lines) with single responsibility
- Use descriptive names following wildfire/ICS terminology
- Comment complex fire behavior algorithms and decision logic

## Core Components

### Discord Bot Integration (`src/discord_wildfire.py`) 
**Sprint 2 Implementation - Singleplayer DM Mode**

#### Context-Aware Command System
- **DM Detection**: Commands automatically detect DM vs Guild context using `interaction.guild is None`
- **Dual Mode Support**: Same commands (`/fire`, `/respond`, `/firestatus`) work differently in each context
- **Clean Routing**: Separate handler functions for singleplayer vs multiplayer modes

#### Singleplayer Game Engine (`SingleplayerGame` class)
- **User Isolation**: Personal game state completely separate from multiplayer
- **Personal Fires**: Individual fire incidents with unique IDs (`personal_{user_id}_{timestamp}`)
- **Solo Progress**: Independent containment and response tracking per user
- **State Management**: Per-user fire tracking and assignment handling

#### Debug Controls (DM-only commands)
- `/clear` - Reset all personal game state for testing/development
- `/start` - Begin new singleplayer scenario session
- `/stop` - End current session cleanly with summary
- **Context Protection**: Debug commands only work in DM context

#### Commands Available
- `/fire` - Create wildfire incident (context-aware: personal vs guild)
- `/respond` - Join incident response (context-aware: solo vs team)  
- `/firestatus` - Check incident status (context-aware: personal vs guild fires)
- `/clear` - Reset personal state (DM only)
- `/start` - Begin new session (DM only)
- `/stop` - End session (DM only)

### Fire Simulation Engine (`src/game/fire_grid.py`)
- Internal 6x6 or 8x8 cellular automata grid (never displayed)
- Terrain types: Forest, Grass, Urban, Ridge, Valley
- Weather effects: wind direction/speed, humidity, temperature
- Fire states: Empty, Burning, Burned, Contained
- Realistic spread rates based on fuel type and conditions

### Resource Management (`src/game/resources.py`)
- Hand Crews: 20 firefighters, high mobility, all terrain
- Helitack: 8 firefighters + helicopter, weather dependent
- Air Tankers: 2,400 gal retardant, create firebreaks
- Dozers: Build fire lines, terrain limited
- Engines: Structure protection, road access required

### Game Loop (`src/game/game_state.py`)
- Turn-based operational periods (12-24 hours)
- ICS planning cycle: briefing → objectives → strategy → allocation → implementation
- Win/loss conditions based on acres burned, structures saved, safety record
- Random events: weather changes, equipment failures, spot fires

### UI Components (`src/ui/`)
- Rich Panel: Incident reports with color coding
- Rich Table: Resource status and availability
- Rich Prompt: Multiple choice tactical decisions
- Report generation: Convert grid state to authentic text reports

## Testing Strategy

### Unit Tests
- Fire spread algorithm accuracy
- Resource deployment effectiveness calculations
- Game state transitions and persistence
- Report generation from simulation data

### Integration Tests
- Complete operational period cycles
- Multi-turn scenario progression
- UI component integration
- Save/load game state functionality

### Educational Testing
- Verify authentic ICS terminology usage
- Validate fire behavior realism
- Test learning objective achievement
- Review tactical decision consequences

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run game locally
python src/main.py

# Run Discord bot locally  
python src/discord_wildfire.py

# Run tests
pytest tests/ --cov=src --cov-report=term-missing

# Code quality
black src/
flake8 src/
mypy src/
```

## Deployment

### DigitalOcean App Platform
**Current Status**: Deployed and Active
- **App ID**: `abd7b01b-a449-4108-ac1a-5c3825a20322`
- **Bot Name**: BlazeBot
- **URL**: https://wildfire-discord-bot-27nzy.ondigitalocean.app
- **Cost**: ~$5/month for basic deployment

### Deployment Commands
```bash
# Deploy new version
doctl apps create-deployment abd7b01b-a449-4108-ac1a-5c3825a20322 --wait

# Check status
doctl apps get abd7b01b-a449-4108-ac1a-5c3825a20322

# View logs
doctl apps logs abd7b01b-a449-4108-ac1a-5c3825a20322 --type run

# Quick deploy script
./deploy.sh
```

### Bot Features Live
✅ **Multiplayer Mode** - Guild-based team firefighting  
✅ **Singleplayer Mode** - DM-based solo training (Sprint 2)  
✅ **Context-Aware Commands** - Same commands, different behavior  
✅ **Debug Controls** - DM-only development tools

## GitHub Project Management

### Sprint Planning
- Use automated sprint planning workflows
- Review velocity and capacity before committing to work
- Focus on one epic per sprint when possible
- Track burndown using story points and issue completion

### Issue Templates
- **User Story**: Feature development with acceptance criteria
- **Bug Report**: Issue tracking with severity classification  
- **Epic**: Large initiatives broken down into stories
- **Sprint Planning**: Organized sprint cycles

### Automation
- Auto-labeling based on issue content and type
- Sprint progress tracking and burndown metrics
- PR linking to related issues
- Velocity calculations and reporting

## Educational Goals

### Learning Objectives
- Understand real wildfire incident command structure
- Learn resource deployment strategies and limitations
- Practice risk assessment and tactical decision making
- Experience realistic fire behavior and consequences

### Authentic Elements
- ICS organizational structure and terminology
- Operational period planning cycles
- Resource types and capabilities
- Weather and terrain effects on fire behavior
- Multi-agency coordination challenges

## Success Metrics

### Technical
- >90% test coverage maintained
- Fire simulation performance <100ms per turn
- UI responsiveness across terminal sizes
- Zero firefighter fatalities in scenarios (mandatory)

### Educational  
- Players learn 10+ ICS terms correctly
- Decision consequences feel realistic
- Multiple valid solutions to scenarios
- Progressive difficulty curve maintained

---

When working on this project, always remember: it's an educational tool that respects the serious nature of wildfire incident command while providing engaging learning experiences through authentic simulation.