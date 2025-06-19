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

### Current Sprint Status
**Sprint 4**: Singleplayer UX Excellence (Issues #22, #23, #24)
- 🎮 Discord Interactive Interface (6 pts) - Rich embeds & decision buttons
- 🎓 Rookie Commander Tutorial (6 pts) - Integrated learning experience  
- ⚡ Real-time Game Feel (6 pts) - Dynamic fire progression
- 📋 Multiplayer Foundation (2 pts) - Architecture planning for Sprint 5

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
- ✅ Automatic wiki management - ✅ Version synchronization - ✅ GitHub web interface
- ✅ PM integration - ✅ Full version control

### Recent Achievements
- **🔥 Complete Fire Simulation Engine** - Cellular automata with realistic behavior
- **📋 Professional ICS Report Generation** - Authentic incident command documentation  
- **🎮 Enhanced Singleplayer Experience** - Complete wildfire training scenarios
- **🚀 Production Deployment** - Bot operational on DigitalOcean

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
# 1. Commit changes
git add . && git commit -m "Description 🤖 Generated with [Claude Code](https://claude.ai/code) Co-Authored-By: Claude <noreply@anthropic.com>"

# 2. Push and deploy
git push
doctl apps create-deployment abd7b01b-a449-4108-ac1a-5c3825a20322 --wait

# 3. Monitor
doctl apps logs abd7b01b-a449-4108-ac1a-5c3825a20322 --type run --follow
```

### Project Management Integration
```bash
# Common PM workflows
gh issue list --state open --json number,title,labels
gh issue create --title "Sprint Planning" --label "sprint-planning"
gh issue edit 123 --add-label "ready-for-sprint"
gh milestone create "Sprint 4" --due-date 2025-07-01
```

### GitHub Project Board Creation & Management

**Repository-Level Project Setup (Completed):**
- **Project:** Wildfire CLI Kanban Board (Project #5)
- **URL:** https://github.com/users/chriswingler/projects/5
- **Repository Link:** ✅ Confirmed appearing in wildfire-cli/projects tab

**GitHub CLI Commands for Repository Projects:**
```bash
# Create repository-linked project
gh project create --owner chriswingler --title "Project Name"

# Link project to repository (critical for repo Projects tab visibility)
gh project link PROJECT_NUMBER --owner chriswingler --repo chriswingler/wildfire-cli

# Add issues to project
gh project item-add PROJECT_NUMBER --owner chriswingler --url https://github.com/chriswingler/wildfire-cli/issues/ISSUE_NUMBER

# List projects for user
gh project list --owner chriswingler

# View project details
gh project view PROJECT_NUMBER --owner chriswingler

# Verify repository integration via GraphQL
gh api graphql -f query='{ repository(owner: "chriswingler", name: "wildfire-cli") { projectsV2(first: 10) { nodes { id number title url } } } }'
```

**Active Project**: Wildfire CLI Kanban Board (Project #5)
- **Integration**: Full kanban workflow with existing label system
- **Current Issues**: Sprint 4 (#22, #23, #24), Epic #20

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

**Kanban Workflow Process:**
1. New Issues → `status: todo` 2. Sprint Planning → Assign iteration/work stream
3. Development → `status: in-progress` 4. Code Review → `status: review` 5. Completed → `status: done`

### Dynamic Kanban Management - MANDATORY FOR CLAUDE

**CRITICAL: Claude MUST actively manage the kanban board during ALL work sessions**

#### Core Requirements
- **Real-time Updates**: Update ticket status immediately when starting, pausing, or completing work
- **Liberal Task Creation**: Create tickets for ANY non-trivial work (>15 minutes estimated)
- **Status Transparency**: Board status must reflect actual work state at all times
- **Zero Statusless Tasks**: ALL new issues MUST be created with status labels

#### Session Startup Workflow
```bash
# Check for statusless items at start of EVERY session
gh project item-list 5 --owner chriswingler --limit 100 --format json | jq -r '.items[] | select(.status == null) | "\(.id)|\(.content.title)"' | wc -l
```

#### Essential Commands
```bash
# Create new task with status
gh issue create --title "Task Title" --body "Description" --label "area: [work-stream],status: ready,iteration: current"

# Add task to project board
gh project item-add 5 --owner chriswingler --url https://github.com/chriswingler/wildfire-cli/issues/ISSUE_NUMBER

# Move task to in-progress
gh project item-edit --project-id PVT_kwHOAhw3ec4A73sX --id ITEM_ID --field-id PVTSSF_lAHOAhw3ec4A73sXzgwCjN0 --single-select-option-id 220d888e

# Mark task as complete
gh project item-edit --project-id PVT_kwHOAhw3ec4A73sX --id ITEM_ID --field-id PVTSSF_lAHOAhw3ec4A73sXzgwCjN0 --single-select-option-id 96476e3e
```

#### Project Field Reference

**Project ID**: `PVT_kwHOAhw3ec4A73sX` (Wildfire CLI Kanban Board)

**Status Field** (`PVTSSF_lAHOAhw3ec4A73sXzgwCjN0`):
- **📋 Backlog**: `e8531425` - **🎯 Ready**: `79a33717` - **🔄 In Progress**: `220d888e`
- **🔍 Review**: `999d0281` - **✅ Done**: `96476e3e` - **🚀 Deployed**: `8ee3614d`

**Priority Field** (`PVTSSF_lAHOAhw3ec4A73sXzgwCsfE`):
- **🔴 High**: `4fc90dfd` - **🟡 Medium**: `142144d8` - **🟢 Low**: `02ee54e0`

**Story Points Field** (`PVTSSF_lAHOAhw3ec4A73sXzgwCsfg`):
- **1**: `67fbe060` - **2**: `e77c913c` - **3**: `56fdd7a0` - **5**: `295144b8` - **8**: `a3e8ef1f` - **13**: `49714513`

#### User Collaboration Through Board Changes
Claude responds to user board changes:
- **Task moved to "In Progress"**: Acknowledge and start work immediately
- **Description edits**: Confirm scope changes and adapt approach
- **Priority changes**: Adjust work plan accordingly
- **Comments added**: Respond to feedback and incorporate guidance

```bash
# Check board state at session start
gh project item-list 5 --owner chriswingler --format json | jq -r '.items[] | select(.status == "In Progress") | .content.title'
```


#### Board Configuration
**Project Board**: https://github.com/users/chriswingler/projects/5

**Manual Setup Required** (GitHub API limitation):
1. Open project board → View Options (⋯) → Group by "Workflow Stage"
2. Result: 6-column workflow: 📋 Backlog | 🎯 Ready | 🔄 In Progress | 🔍 Review | ✅ Done | 🚀 Deployed

**Troubleshooting**: If CLI commands fail, use GitHub web interface as fallback

### Sprint & Issue Management
- **Sprint Planning**: Claude manages velocity tracking and capacity planning
- **Issue Types**: User Story, Bug Report, Epic, Sprint Planning
- **Automation**: Sprint reviews, automated updates, epic breakdown, real-time coordination

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