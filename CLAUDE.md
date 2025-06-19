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
│   ├── game/              # Core game logic and simulation
│   ├── ui/                # Rich library interface components  
│   └── scenarios/         # Game content and decision trees
├── data/                  # Scenario configurations (JSON)
├── tests/                 # Unit and integration tests
├── docs/                  # Project documentation
└── .github/               # GitHub automation and templates
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

# Run game
python src/main.py

# Run tests
pytest tests/ --cov=src --cov-report=term-missing

# Code quality
black src/
flake8 src/
mypy src/
```

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