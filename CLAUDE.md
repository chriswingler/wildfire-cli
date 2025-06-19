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
│   ├── fire_engine.py        # Complete cellular automata fire simulation (Sprint 3)
│   ├── incident_reports.py   # Professional ICS report generation (Sprint 3)
│   ├── game/                 # Core game logic and simulation
│   ├── ui/                   # Rich library interface components  
│   └── scenarios/            # Game content and decision trees
├── wiki/                     # Development wiki (GitHub submodule)
│   ├── Home.md              # Development dashboard
│   ├── Sprint-Planning.md   # PM workflows and ceremonies
│   ├── Kanban-Workflow.md   # GitHub project board usage
│   ├── Technical-Architecture.md # System design and decisions
│   ├── Development-Standards.md  # Code quality and conventions
│   ├── Troubleshooting.md   # Common issues and solutions
│   ├── Velocity-Analysis.md # Sprint metrics and capacity planning
│   └── Deployment-Guide.md  # Production deployment workflows
├── data/                     # Scenario configurations (JSON)
├── tests/                    # Unit and integration tests
├── .do/                      # DigitalOcean deployment configuration
└── .github/                  # GitHub automation and templates
```

## Development Workflow

### Agile Process (Claude-Managed)
- **Sprints**: 2-week cycles with adaptive capacity (16-25 story points proven)
- **Planning**: Claude manages GitHub issues with story points, epics, and sprint planning
- **Reviews**: Claude provides sprint retrospectives with velocity analysis
- **Testing**: >90% code coverage required, emphasis on fire simulation accuracy
- **PM Leadership**: Claude acts as Product Manager using GitHub CLI for project coordination

### Issue Management (Claude-Driven)
- **Claude creates and manages** user stories, bugs, epics with proper formatting
- **Automated sprint planning** with capacity analysis and risk assessment
- **Dynamic scope adjustment** based on technical implementation discoveries
- **Real-time project updates** through GitHub CLI issue management
- **Epic breakdown** by Claude into manageable user stories with dependencies
- **Velocity tracking** across sprints with burndown analysis

### Sprint History & Velocity
- **Sprint 1**: Foundation - Discord bot basics (completed)
- **Sprint 2**: Singleplayer DM Mode - 16 story points (completed) 
- **Sprint 3**: Core Simulation Engine - 25+ story points (✅ MAJOR SUCCESS)
- **Sprint 4**: Singleplayer UX Excellence - 20 story points (🔄 REPRIORITIZED)
- **Sprint 5**: Enhanced Multiplayer - 20 story points (planned)
- **Average Velocity**: 25+ story points per sprint (significantly exceeded estimates)

### Sprint 4 Reprioritization (Critical UX Fix)
**Problem Identified:** Sprint 3 delivered excellent technical foundation but poor user experience
- ❌ Code blocks instead of rich Discord embeds
- ❌ Information dumps vs progressive learning
- ❌ No interactive decision buttons
- ❌ Turn-based vs real-time incident feel

**Sprint 4 Solution:** Singleplayer UX Excellence (Issues #22, #23, #24)
- 🎮 Discord Interactive Interface (6 pts) - Rich embeds & decision buttons
- 🎓 Rookie Commander Tutorial (6 pts) - Integrated learning experience  
- ⚡ Real-time Game Feel (6 pts) - Dynamic fire progression
- 📋 Multiplayer Foundation (2 pts) - Architecture planning for Sprint 5

**Epic #20 Deferred:** Enhanced Multiplayer moved to Sprint 5 after UX foundation complete

## Wiki Submodule Integration

### **GitHub Wiki as Submodule**
The project uses the GitHub wiki as a Git submodule for automatic development documentation management:

```bash
# Wiki submodule setup (completed)
git submodule add https://github.com/chriswingler/wildfire-cli.wiki.git wiki
git submodule update --init --recursive
```

### **Submodule Workflow**
**Developer workflow integrates wiki updates with code changes:**

```bash
# Working with wiki submodule (automatic management)
cd wildfire-cli/
# Edit both code and wiki/ documentation
git add src/ wiki/
git commit -m "Feature implementation + wiki update"
git push --recurse-submodules=on-demand
# Both main repo and wiki automatically updated
```

### **Wiki Content Organization**
**Internal development documentation structure:**
- **[Home](wiki/Home.md)** - Development dashboard with current sprint status
- **[Sprint Planning](wiki/Sprint-Planning.md)** - PM workflows and sprint ceremonies  
- **[Kanban Workflow](wiki/Kanban-Workflow.md)** - GitHub project board usage and labels
- **[Technical Architecture](wiki/Technical-Architecture.md)** - System design and technical decisions
- **[Development Standards](wiki/Development-Standards.md)** - Code quality standards and conventions
- **[Troubleshooting](wiki/Troubleshooting.md)** - Common development issues and solutions
- **[Velocity Analysis](wiki/Velocity-Analysis.md)** - Sprint metrics and capacity planning
- **[Deployment Guide](wiki/Deployment-Guide.md)** - Production deployment workflows

### **Benefits of Submodule Approach**
- ✅ **Automatic wiki management** - No separate workflows needed
- ✅ **Version synchronization** - Wiki and code stay in sync
- ✅ **GitHub web interface** - Still accessible via GitHub wiki UI
- ✅ **PM integration** - Wiki updates part of sprint workflow
- ✅ **Full version control** - Complete Git workflow for documentation

### Sprint 3 Major Achievements
- **🔥 Complete Fire Simulation Engine** - Cellular automata with realistic behavior
- **📋 Professional ICS Report Generation** - Authentic incident command documentation  
- **🎮 Enhanced Singleplayer Experience** - Complete wildfire training scenarios
- **🔧 Global Command Sync** - Fixed DM command functionality for OAuth scopes
- **🚀 Production Deployment** - Bot operational with clean logging

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

### Deployment Workflow

**CRITICAL: Always commit and push before deploying**

```bash
# 1. Make code changes
# 2. Test locally if possible
# 3. Stage and commit changes
git add .
git commit -m "Description of changes

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 4. Push to repository
git push

# 5. Deploy to DigitalOcean
doctl apps create-deployment abd7b01b-a449-4108-ac1a-5c3825a20322

# 6. Monitor deployment
doctl apps get abd7b01b-a449-4108-ac1a-5c3825a20322
doctl apps logs abd7b01b-a449-4108-ac1a-5c3825a20322 --type run --follow
```

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

### Project Management Integration
```bash
# Common PM workflows Claude uses
gh issue list --state open --json number,title,labels
gh issue create --title "Sprint Planning" --label "sprint-planning"
gh issue close 123 --comment "Sprint completed with all acceptance criteria met"
gh issue edit 123 --add-label "ready-for-sprint"

# Sprint velocity tracking
gh issue comment 19 "Sprint 3: 25+ story points delivered (exceeded capacity)"
gh milestone create "Sprint 4" --due-date 2025-07-01 --description "Enhanced Multiplayer"
```

### Bot Features Live
✅ **Complete Fire Simulation** - Cellular automata engine with realistic behavior (Sprint 3)
✅ **Professional ICS Reports** - Authentic incident command documentation (Sprint 3)  
✅ **Enhanced Singleplayer Mode** - Complete wildfire training scenarios (Sprint 3)
✅ **Multiplayer Mode** - Guild-based team firefighting (foundational)
✅ **Context-Aware Commands** - Same commands, different behavior in DM vs Guild
✅ **Global Command Sync** - DM slash commands working properly (Sprint 3)
✅ **Production Deployment** - Bot operational on DigitalOcean (Sprint 3)

## Project Management with Claude Code

### Claude's Product Manager Capabilities
**Claude Code has full GitHub CLI access and skilled PM abilities for project management:**

#### GitHub Repository Management (via `gh` CLI)
- **Issue Management**: Create, edit, close, comment on issues
- **Sprint Planning**: Organize sprints, manage backlogs, track velocity  
- **Epic Management**: Break down large features into user stories
- **Label Management**: Apply and manage issue labels for organization
- **Milestone Tracking**: Set up and track sprint milestones
- **Project Coordination**: Coordinate work across team members

#### Product Management Skills
- **Agile Planning**: Sprint planning, backlog grooming, velocity tracking
- **User Story Writing**: Acceptance criteria, story point estimation
- **Epic Breakdown**: Large feature decomposition into manageable tasks  
- **Risk Assessment**: Technical dependencies and delivery risks
- **Stakeholder Communication**: Progress updates and delivery planning
- **Quality Assurance**: Definition of Done, acceptance criteria validation

#### GitHub CLI Commands Available
```bash
# Issue Management
gh issue create --title "User Story" --body "Description" --label "user-story"
gh issue edit 123 --add-label "ready-for-sprint" --milestone "Sprint 4"
gh issue close 123 --comment "Completed with acceptance criteria met"
gh issue list --state open --label "sprint-planning"

# Sprint Planning  
gh issue create --title "🏃 Sprint X Planning" --label "sprint-planning"
gh issue comment 123 "Sprint velocity: 20 points completed"
gh milestone create "Sprint 4" --due-date 2025-07-01

# Project Organization
gh label create "epic" --description "Large feature initiative" --color "5319E7"
gh issue view 123 --json body,labels,assignees
```

#### GitHub Project Kanban Board Structure
**Claude has set up a comprehensive GitHub project with kanban workflow for visual project management:**

**Work Stream Labels (for categorization):**
- `area: ui-ux` - User interface and experience work stream
- `area: game-engine` - Core game logic and simulation work stream  
- `area: content` - Game content and scenarios work stream
- `area: infrastructure` - Architecture, deployment, and tooling work stream

**Status Labels (for kanban workflow):**
- `status: todo` - Ready to start work (purple)
- `status: in-progress` - Currently being worked on (yellow)
- `status: review` - Code review or testing needed (orange)
- `status: done` - Completed and deployed (green)

**Iteration Labels (for sprint grouping):**
- `iteration: current` - Current sprint (Sprint 4)
- `iteration: next` - Next sprint (Sprint 5)  
- `iteration: future` - Future sprint planning

**GitHub Project Board Views:**
1. **Main Board View** - Grouped by work streams for quick categorization
2. **Sprint Board View** - Grouped by iterations for sprint planning
3. **Kanban Board View** - Grouped by status for workflow management
4. **Feature Focus View** - Filter by user-story label for feature work

**Project Board Usage:**
```bash
# Add work stream and status labels to issues
gh issue edit 22 --add-label "area: ui-ux,status: todo,iteration: current"

# Move items through kanban workflow
gh issue edit 22 --remove-label "status: todo" --add-label "status: in-progress"

# Sprint planning with iteration management
gh issue edit 20 --add-label "iteration: next" --milestone "Sprint 5"

# Quick issue creation with proper categorization
gh issue create --title "New Feature" --label "user-story,area: ui-ux,status: todo"
```

**Kanban Workflow Process:**
1. **New Issues** → `status: todo` (ready for sprint planning)
2. **Sprint Planning** → Assign to iteration and work stream
3. **Development** → Move to `status: in-progress` 
4. **Code Review** → Move to `status: review`
5. **Completed** → Move to `status: done` and close issue

### Sprint Planning Process
- **Claude manages sprint planning issues** with velocity tracking
- **Auto-close completed issues** with detailed completion summaries
- **Create new sprints** with capacity planning and risk assessment
- **Update issue scope** based on technical discoveries and dependencies
- **Track burndown** using story points and delivery metrics

### Issue Templates & Organization
- **User Story**: Feature development with acceptance criteria (Claude creates)
- **Bug Report**: Issue tracking with severity classification  
- **Epic**: Large initiatives broken down by Claude into stories
- **Sprint Planning**: Claude-managed sprint cycles with velocity tracking

### Automation & Tracking
- **Claude-driven sprint reviews** with velocity and completion analysis
- **Automated issue updates** based on technical implementation progress
- **Epic breakdown management** with dependency tracking
- **Real-time project coordination** through GitHub CLI integration

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