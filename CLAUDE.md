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

**Key Lessons Learned:**
1. **GitHub Projects V2 are user/org-level** by default, not repository-level
2. **Repository linking is separate step** - use `gh project link` command
3. **User projects don't appear in repo Projects tab** without explicit linking
4. **GraphQL createProjectV2 with repository node ID fails** - use GitHub CLI instead
5. **GitHub CLI project commands are more reliable** than direct GraphQL for repo integration

**Project Management Workflow:**
```bash
# Complete repository project setup workflow
PROJECT_NUM=$(gh project create --owner chriswingler --title "New Project" --format json | jq -r '.number')
gh project link $PROJECT_NUM --owner chriswingler --repo chriswingler/wildfire-cli
gh project item-add $PROJECT_NUM --owner chriswingler --url https://github.com/chriswingler/wildfire-cli/issues/ISSUE_NUM
```

**Current Active Project:**
- **Project #5:** Wildfire CLI Kanban Board
- **Issues Added:** Sprint 4 (#22, #23, #24), Epic #20, completed items
- **Integration:** Full kanban workflow with existing label system
- **Status:** Ready for Sprint 4 execution with visual project management

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

### Dynamic Kanban Management Rules - MANDATORY FOR CLAUDE

**CRITICAL: Claude MUST actively manage the kanban board during ALL work sessions**

#### 🚨 SESSION STARTUP REQUIREMENTS
**MANDATORY FIRST STEP**: Check for statusless items before any other work:
```bash
# REQUIRED: Run this command at start of EVERY session
gh project item-list 5 --owner chriswingler --limit 100 --format json | jq -r '.items[] | select(.status == null) | "\(.id)|\(.content.title)"' | wc -l

# If ANY statusless items found: FIX IMMEDIATELY before proceeding with other work
```

#### Core Board Management Requirements
- **Real-time Updates**: Update ticket status immediately when starting, pausing, or completing work
- **Liberal Task Creation**: Create tickets for ANY non-trivial work (>15 minutes estimated)
- **Frequent Board Activity**: User should see kanban changes throughout work sessions
- **Granular Tracking**: Break large tasks into smaller, trackable subtasks
- **Status Transparency**: Board status must reflect actual work state at all times

#### When Claude MUST Create New Issues
- **Feature Development**: Any new feature or enhancement work
- **Bug Fixes**: Any bug investigation or resolution work
- **Research Tasks**: Technical research, exploration, or analysis
- **Refactoring Work**: Code cleanup, optimization, or restructuring
- **Documentation**: Writing or updating documentation
- **Testing**: Creating or updating tests
- **Configuration**: Environment, deployment, or setup changes
- **Subtasks**: Breaking down complex work into manageable pieces

**⚠️ CRITICAL: ALL new issues MUST be created with status labels - NEVER create issues without status assignment!**

#### Required Status Update Triggers
- **Work Start**: Move ticket to `status: in-progress` when beginning work
- **Work Pause**: Comment with current progress when pausing/switching tasks
- **Blocking Issues**: Update status and comment when blocked or waiting
- **Work Complete**: Move to `status: review` or `status: done` immediately
- **Scope Changes**: Update ticket description when scope or approach changes
- **New Discoveries**: Create new tickets for discovered work

#### Project Board Commands (Claude Must Use Frequently)
```bash
# REQUIRED: Mark task as in-progress when starting work
gh project item-edit --project-id PVT_kwHOAhw3ec4A73sX --id ITEM_ID --field-id PVTSSF_lAHOAhw3ec4A73sXzgwCjN0 --single-select-option-id 47fc9ee4

# REQUIRED: Mark task as done when completing work  
gh project item-edit --project-id PVT_kwHOAhw3ec4A73sX --id ITEM_ID --field-id PVTSSF_lAHOAhw3ec4A73sXzgwCjN0 --single-select-option-id 98236657

# REQUIRED: Create new task for any non-trivial work (ALWAYS with status!)
gh issue create --title "Task Title" --body "Description" --label "area: [work-stream],status: in-progress,iteration: current"

# ⚠️ CRITICAL: NEVER create issues without status - always include status in labels!

# REQUIRED: Add new tasks to project board immediately
gh project item-add 5 --owner chriswingler --url https://github.com/chriswingler/wildfire-cli/issues/ISSUE_NUMBER

# REQUIRED: Update task status when work state changes
gh issue comment ISSUE_NUMBER "Progress update: [current status and next steps]"

# REQUIRED: Close completed tasks with summary
gh issue close ISSUE_NUMBER --comment "Completed: [summary of work done and results]"
```

#### Board Activity Expectations
- **Multiple Updates Per Session**: 3-5 board updates during typical work session
- **Granular Task Breakdown**: Large tasks broken into 2-4 hour chunks
- **Progress Comments**: Regular progress updates on in-progress tickets
- **Immediate Status Changes**: No delay between work state and board state
- **Proactive Task Creation**: Create tickets before starting work, not after

#### ⚠️ MANDATORY STATUS ASSIGNMENT - NO EXCEPTIONS

**CRITICAL RULE: Every task MUST have a status assigned - NEVER allow "No Status" items**

#### Mandatory Status Assignment Requirements
- **100% Status Coverage**: Every task created must immediately receive a status
- **No "No Status" Column**: The "No Status" column should NEVER contain items
- **Real-time Assignment**: Status must be assigned within seconds of task creation
- **Automatic Prevention**: Use labels and automation to prevent statusless tasks
- **Board Hygiene**: Regular audits to catch and fix any statusless items

#### Required Status Assignment Workflow
```bash
# MANDATORY: Always assign status when creating tasks
gh issue create --title "Task Title" --body "Description" --label "area: [work-stream],status: todo,iteration: current"

# MANDATORY: Immediately assign status to any existing statusless tasks
gh project item-list 5 --owner chriswingler --limit 100 --format json | jq -r '.items[] | select(.status == null) | "\(.id)|\(.content.title)"'

# MANDATORY: Fix statusless items immediately when found
gh project item-edit --project-id PVT_kwHOAhw3ec4A73sX --id ITEM_ID --field-id PVTSSF_lAHOAhw3ec4A73sXzgwCjN0 --single-select-option-id [STATUS_ID]
```

#### Status Assignment Decision Matrix
- **New Ideas/Future Work**: `📋 Backlog` (`e8531425`)
- **Well-Defined & Ready**: `🎯 Ready` (`79a33717`)  
- **Currently Working**: `🔄 In Progress` (`220d888e`)
- **Needs Testing/Review**: `🔍 Review` (`999d0281`)
- **Implementation Complete**: `✅ Done` (`96476e3e`)
- **Live in Production**: `🚀 Deployed` (`8ee3614d`)

#### Default Status Assignment Rules
- **Brainstorming/Ideas**: Default to `📋 Backlog`
- **Sprint Tasks**: Default to `🎯 Ready` 
- **Active Work**: Immediately move to `🔄 In Progress`
- **Bug Reports**: Default to `🎯 Ready` (if actionable) or `📋 Backlog` (if not urgent)
- **Completed Work**: Immediately move to `✅ Done` or `🚀 Deployed`

#### Board Hygiene Enforcement
```bash
# MANDATORY: Check for statusless items at session start
STATUSLESS_COUNT=$(gh project item-list 5 --owner chriswingler --limit 100 --format json | jq -r '.items[] | select(.status == null)' | wc -l)
if [ "$STATUSLESS_COUNT" -gt 0 ]; then
    echo "❌ CRITICAL: $STATUSLESS_COUNT tasks without status found - fixing immediately"
    # Fix all statusless items before proceeding with other work
fi

# MANDATORY: Audit board weekly for process improvements
gh project item-list 5 --owner chriswingler --limit 100 --format json | jq -r '.items[] | "\(.status) | \(.content.title)"' | sort | uniq -c
```

#### Zero Tolerance Policy
- **No statusless tasks allowed EVER**
- **Immediate correction required when found**
- **Process failure when "No Status" column has items**
- **Board hygiene is non-negotiable project standard**

#### Field Reference - Enhanced Kanban Board

**Project Information:**
- **Project ID**: `PVT_kwHOAhw3ec4A73sX` (Wildfire CLI Kanban Board)

**Status Field** (`PVTSSF_lAHOAhw3ec4A73sXzgwCjN0`) - OPTIMIZED 6-COLUMN WORKFLOW:
- **📋 Backlog**: `e8531425` (purple - future/undefined tasks awaiting planning)
- **🎯 Ready**: `79a33717` (blue - well-defined tasks ready to start work)
- **🔄 In Progress**: `220d888e` (yellow - tasks currently being worked on)
- **🔍 Review**: `999d0281` (orange - code review and testing needed)
- **✅ Done**: `96476e3e` (green - implementation complete)
- **🚀 Deployed**: `8ee3614d` (red - live in production)

**Priority Field** (`PVTSSF_lAHOAhw3ec4A73sXzgwCsfE`):
- **🔴 High**: `4fc90dfd` (urgent tasks requiring immediate attention)
- **🟡 Medium**: `142144d8` (important tasks for current sprint)
- **🟢 Low**: `02ee54e0` (future tasks and nice-to-have features)

**Story Points Field** (`PVTSSF_lAHOAhw3ec4A73sXzgwCsfg`):
- **1**: `67fbe060` (trivial task, 1-2 hours)
- **2**: `e77c913c` (small task, 2-4 hours)
- **3**: `56fdd7a0` (medium task, 4-8 hours)
- **5**: `295144b8` (large task, 1-2 days)
- **8**: `a3e8ef1f` (very large task, 2-3 days)
- **13**: `49714513` (epic-sized task, 1 week+)

**Workflow Stage Field** (`PVTSSF_lAHOAhw3ec4A73sXzgwCsiY`):
- **📋 Backlog**: `6456d3de` (future/undefined tasks awaiting planning)
- **🎯 Ready**: `118de8ea` (well-defined tasks ready to start)
- **🔄 In Progress**: `8c9956c9` (tasks currently being worked on)
- **🔍 Review**: `5e3b8bb3` (code review and testing needed)
- **✅ Done**: `2a2bdd21` (implementation complete)
- **🚀 Deployed**: `43ef1ad8` (live in production)

#### Real-time Board Management Examples
```bash
# Starting work on a feature
gh issue create --title "Implement fire spread algorithm optimization" --label "area: game-engine,status: in-progress,iteration: current"
gh project item-add 5 --owner chriswingler --url https://github.com/chriswingler/wildfire-cli/issues/NEW_ISSUE

# Discovering additional work needed
gh issue create --title "Add unit tests for fire spread optimization" --label "area: game-engine,status: todo,iteration: current"

# Completing work with detailed summary
gh issue close 123 --comment "Completed: Fire spread algorithm optimized. Performance improved by 40%. All tests passing. Ready for deployment."

# Moving to next task
gh project item-edit --project-id PVT_kwHOAhw3ec4A73sX --id NEXT_ITEM_ID --field-id PVTSSF_lAHOAhw3ec4A73sXzgwCjN0 --single-select-option-id 47fc9ee4
```

**RESULT: User will see live kanban board activity as Claude works, providing complete transparency into development progress and current focus areas.**

#### Bidirectional Kanban Interaction - MANDATORY

**CRITICAL: Claude MUST detect and respond to user-initiated board changes**

#### Session Startup Board Assessment
- **REQUIRED**: Check current board state at the start of every work session
- **REQUIRED**: Compare board state with previous session expectations
- **REQUIRED**: Acknowledge any user changes, moves, or reorganizations
- **REQUIRED**: Ask for clarification when user changes impact planned work
- **REQUIRED**: Adapt work priorities based on user board manipulation

#### Detecting User Signals Through Board Changes
Claude must recognize these user communication patterns:

**User Moves Task to "In Progress"**: 
- User is requesting Claude work on this task immediately
- Claude should acknowledge and either start work or explain any blockers

**User Moves Task Between Columns**: 
- User is signaling priority or status changes
- Claude should acknowledge the change and adjust planning accordingly

**User Edits Task Description/Title**:
- User is changing scope, requirements, or approach
- Claude should read changes and confirm understanding

**User Adds Comments to Tasks**:
- User is providing guidance, feedback, or new requirements
- Claude should respond to comments and incorporate feedback

**User Changes Task Labels/Iteration**:
- User is reorganizing priorities or sprint planning
- Claude should acknowledge and adapt work planning

#### Required User Change Response Patterns
```bash
# REQUIRED: Check board state at session start
gh project item-list 5 --owner chriswingler --format json | jq -r '.items[] | select(.status == "In Progress") | .content.title'

# REQUIRED: Acknowledge user priority changes
gh issue comment ISSUE_NUMBER "Acknowledged: User moved this task to high priority. Adjusting work plan accordingly."

# REQUIRED: Respond to user task assignments
gh issue comment ISSUE_NUMBER "Starting work: User moved this task to in-progress. Beginning implementation now."

# REQUIRED: Confirm scope changes
gh issue comment ISSUE_NUMBER "Scope update noted: [summarize user changes]. Confirming new approach: [plan]."
```

#### Collaborative Decision Making Through Board State
The kanban board becomes a communication channel where:

**User Actions Signal Intent**:
- Moving task up in priority = "work on this next"
- Moving task to in-progress = "start this now"  
- Editing description = "change approach or scope"
- Adding comments = "here's guidance or feedback"
- Changing iteration = "this belongs in different sprint"

**Claude Responses Confirm Understanding**:
- Acknowledge user changes immediately
- Ask clarifying questions when changes create conflicts
- Provide status updates on user-requested work
- Suggest alternatives when user requests conflict with technical constraints
- Keep user informed about impact of their changes

#### Session Startup Workflow Example
```bash
# 1. Check for any in-progress tasks (user may have moved something)
gh project item-list 5 --owner chriswingler --format json | jq '.items[] | select(.fieldValues[] | select(.field.name == "Status" and .name == "In Progress"))'

# 2. Check for recent comments or changes
gh issue list --state open --limit 10 --json number,title,updatedAt,comments

# 3. Acknowledge any user changes found
gh issue comment ISSUE_NUMBER "Session startup: Detected user changes to board. Adapting work plan to prioritize user-moved tasks."

# 4. Proceed with work based on current board state
```

#### User Communication Examples

**Scenario 1: User moves task to "In Progress"**
- Claude: "Detected: User moved 'Fix Discord embed formatting' to in-progress. Starting work on this task immediately."
- Claude: Creates implementation subtasks, updates progress, completes work

**Scenario 2: User edits task description** 
- Claude: "Scope change detected: User updated requirements for mobile responsiveness. New approach: [summarized plan]. Proceeding with updated implementation."

**Scenario 3: User changes iteration labels**
- Claude: "Sprint reorganization detected: User moved 3 tasks from Sprint 5 to current iteration. Adjusting capacity planning and work priorities."

**RESULT: True collaborative project management where user and Claude communicate through board state changes, creating seamless workflow coordination.**

#### Enhanced Board Management Commands (UPDATED WITH NEW COLUMNS)

**BREAKTHROUGH**: Successfully added enhanced columns programmatically using \`updateProjectV2Field\`!

**Move Tasks Through Optimized 6-Column Workflow:**
```bash
# Move task to Backlog (future/undefined tasks)
gh project item-edit --project-id PVT_kwHOAhw3ec4A73sX --id ITEM_ID --field-id PVTSSF_lAHOAhw3ec4A73sXzgwCjN0 --single-select-option-id e8531425

# Move task to Ready (well-defined, ready to start)
gh project item-edit --project-id PVT_kwHOAhw3ec4A73sX --id ITEM_ID --field-id PVTSSF_lAHOAhw3ec4A73sXzgwCjN0 --single-select-option-id 79a33717

# Move task to In Progress (active work)
gh project item-edit --project-id PVT_kwHOAhw3ec4A73sX --id ITEM_ID --field-id PVTSSF_lAHOAhw3ec4A73sXzgwCjN0 --single-select-option-id 220d888e

# Move task to Review (code review/testing needed)
gh project item-edit --project-id PVT_kwHOAhw3ec4A73sX --id ITEM_ID --field-id PVTSSF_lAHOAhw3ec4A73sXzgwCjN0 --single-select-option-id 999d0281

# Move task to Done (implementation complete)
gh project item-edit --project-id PVT_kwHOAhw3ec4A73sX --id ITEM_ID --field-id PVTSSF_lAHOAhw3ec4A73sXzgwCjN0 --single-select-option-id 96476e3e

# Move task to Deployed (live in production)
gh project item-edit --project-id PVT_kwHOAhw3ec4A73sX --id ITEM_ID --field-id PVTSSF_lAHOAhw3ec4A73sXzgwCjN0 --single-select-option-id 8ee3614d
```

**Set Priority for Tasks:**
```bash
# Set task to High Priority
gh project item-edit --project-id PVT_kwHOAhw3ec4A73sX --id ITEM_ID --field-id PVTSSF_lAHOAhw3ec4A73sXzgwCsfE --single-select-option-id 4fc90dfd

# Set task to Medium Priority  
gh project item-edit --project-id PVT_kwHOAhw3ec4A73sX --id ITEM_ID --field-id PVTSSF_lAHOAhw3ec4A73sXzgwCsfE --single-select-option-id 142144d8
```

**Set Story Points for Velocity Tracking:**
```bash
# Set task to 3 story points (medium task, 4-8 hours)
gh project item-edit --project-id PVT_kwHOAhw3ec4A73sX --id ITEM_ID --field-id PVTSSF_lAHOAhw3ec4A73sXzgwCsfg --single-select-option-id 56fdd7a0

# Set task to 5 story points (large task, 1-2 days)
gh project item-edit --project-id PVT_kwHOAhw3ec4A73sX --id ITEM_ID --field-id PVTSSF_lAHOAhw3ec4A73sXzgwCsfg --single-select-option-id 295144b8
```

**Use Enhanced Workflow Pipeline:**
```bash
# Move task to Ready (well-defined, ready to start)
gh project item-edit --project-id PVT_kwHOAhw3ec4A73sX --id ITEM_ID --field-id PVTSSF_lAHOAhw3ec4A73sXzgwCsiY --single-select-option-id 118de8ea

# Move task to Review (code review/testing needed)
gh project item-edit --project-id PVT_kwHOAhw3ec4A73sX --id ITEM_ID --field-id PVTSSF_lAHOAhw3ec4A73sXzgwCsiY --single-select-option-id 5e3b8bb3

# Move task to Deployed (live in production)
gh project item-edit --project-id PVT_kwHOAhw3ec4A73sX --id ITEM_ID --field-id PVTSSF_lAHOAhw3ec4A73sXzgwCsiY --single-select-option-id 43ef1ad8
```

#### Kanban Workflow Troubleshooting (CRITICAL FIXES)

**Issue: Project Items Not Adding to Board**
- Problem: `gh project item-add` succeeds but items don't appear on board
- Fix: Wait 5+ seconds after adding, verify with item count check
- Workaround: Use GitHub web interface to manually add items

**Issue: Project Item IDs Not Found**  
- Problem: Status update commands fail with "node not found" errors
- Fix: Use most recent item listing and verify IDs before updating
- Workaround: Use GitHub web interface to manually move items

**Issue: Active Task Tracking Failures**
- Problem: Current work not visible in "In Progress" column
- Fix: Always verify status updates completed successfully
- Workaround: Manually move tasks via web interface when CLI fails

**Manual Fallback Procedure:**
1. Open GitHub project board in web browser
2. Manually drag tasks to appropriate columns
3. Use web interface to set Priority and Story Points fields
4. Add comments to issues for progress tracking
5. Return to CLI when board state is correct

**CRITICAL**: When CLI fails, always use manual workaround to maintain board transparency

#### Board Layout Configuration (MANUAL REQUIRED)

**GitHub API Limitation**: Board view configuration cannot be done programmatically. Manual setup required via web interface.

**To Enable Enhanced 6-Column Workflow:**
1. Open project board: https://github.com/users/chriswingler/projects/5
2. Click View Options (⋯) in top right corner
3. Select "Group by" → "Workflow Stage" (instead of Status)
4. Result: 6-column enhanced pipeline:
   ```
   📋 Backlog | 🎯 Ready | 🔄 In Progress | 🔍 Review | ✅ Done | 🚀 Deployed
   ```

**Additional Recommended Views:**
- **Sprint View**: Group by Labels (filter: iteration: current/next/future)
- **Priority View**: Group by Priority field (High/Medium/Low)
- **Work Stream View**: Group by Labels (filter: area: ui-ux/game-engine/content/infrastructure)
- **Epic View**: Filter by Labels (epic only)

**Task Migration After Layout Change:**
- Current Sprint 4 tasks → 🎯 Ready or 🔄 In Progress
- Future sprint tasks → 📋 Backlog  
- Completed work → ✅ Done or 🚀 Deployed
- Add Priority and Story Points to all tasks for better organization

**Enhanced Board Benefits After Configuration:**
- Clear workflow progression with quality gates
- Priority-based task organization
- Velocity tracking through story points
- Multiple perspectives through different views
- Professional development pipeline

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