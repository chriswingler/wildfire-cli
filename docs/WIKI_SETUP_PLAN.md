# 📚 GitHub Wiki Setup Plan

This document outlines the comprehensive wiki structure for the wildfire-cli project and provides content for each wiki page.

## Wiki Structure Overview

```
📚 Wildfire CLI Wiki
├── 🏠 Home
├── 🚀 Getting Started
├── 👥 For Users
│   ├── How to Play
│   ├── Game Scenarios
│   └── Learning Objectives
├── 👨‍💻 For Developers
│   ├── Setup & Installation
│   ├── Architecture Overview
│   ├── Contributing Guide
│   └── Code Standards
├── 📋 Project Management
│   ├── Agile Process
│   ├── Sprint Ceremonies
│   └── Issue Templates
├── 🔧 Troubleshooting
│   ├── Common Issues
│   ├── Workflow Debugging
│   └── Environment Setup
├── 📊 Resources
│   ├── ICS Terminology
│   ├── Wildfire Basics
│   └── External Resources
└── 🗺️ Roadmap & FAQ
```

## Wiki Pages Content

### 🏠 Home.md
```markdown
# 🔥 Welcome to Wildfire CLI

**A text-based wildfire incident commander simulation game that teaches real-world firefighting tactics and decision-making.**

![Project Status](https://img.shields.io/badge/Status-In%20Development-yellow)
![Sprint](https://img.shields.io/badge/Sprint-1%20Foundation-blue)
![Version](https://img.shields.io/badge/Version-v0.1--dev-red)

## What is Wildfire CLI?

Wildfire CLI is an educational simulation game that puts you in the role of a wildfire Incident Commander. Using authentic Incident Command System (ICS) protocols, you'll make tactical decisions about resource deployment, risk management, and strategic planning while managing realistic fire scenarios.

### 🎯 Key Features

- **Authentic ICS Protocols** - Based on real wildfire incident command structure
- **Text-Only Interface** - Professional terminal UI using Rich library
- **Educational Focus** - Learn actual emergency management principles
- **Progressive Scenarios** - From grass fires to complex multi-agency incidents
- **Decision Consequences** - Realistic outcomes based on tactical choices

### 🚀 Quick Navigation

**For Users:**
- [🎮 How to Play](How-to-Play) - Game instructions and controls
- [📚 Learning Objectives](Learning-Objectives) - What you'll learn
- [🎬 Game Scenarios](Game-Scenarios) - Available fire scenarios

**For Developers:**
- [⚡ Getting Started](Getting-Started) - Quick setup guide
- [🏗️ Architecture Overview](Architecture-Overview) - Technical design
- [🤝 Contributing Guide](Contributing-Guide) - How to contribute

**Project Resources:**
- [📋 Agile Process](Agile-Process) - How we work
- [🔧 Troubleshooting](Troubleshooting) - Common issues and solutions
- [🗺️ Roadmap](Roadmap) - Future plans and milestones

### 📞 Getting Help

- 🐛 **Found a bug?** Create an [Issue](https://github.com/chriswingler/wildfire-cli/issues/new?template=bug_report.yml)
- 💡 **Have an idea?** Start a [Discussion](https://github.com/chriswingler/wildfire-cli/discussions)
- 📖 **Need help?** Check our [FAQ](FAQ) or [Troubleshooting](Troubleshooting) guides

---

*This project teaches the serious nature of wildfire incident command while providing engaging learning experiences through authentic simulation.*
```

### 🚀 Getting-Started.md
```markdown
# 🚀 Getting Started

This guide helps you set up the wildfire-cli project for development or use.

## Prerequisites

- **Python 3.8+** - Required for running the game
- **Git** - For cloning the repository
- **Terminal** - Command-line interface
- **GitHub Account** - For contributing to development

## Quick Setup

### 1. Clone the Repository
```bash
git clone https://github.com/chriswingler/wildfire-cli.git
cd wildfire-cli
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Game
```bash
python src/main.py
```

## Development Setup

### 1. Set Up Development Environment
```bash
# Install development dependencies
pip install -r requirements-dev.txt  # When available

# Install pre-commit hooks
pre-commit install  # If configured
```

### 2. Run Tests
```bash
# Run all tests
pytest tests/ --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_fire_simulation.py -v
```

### 3. Code Quality Checks
```bash
# Format code
black src/

# Check style
flake8 src/

# Type checking
mypy src/
```

## Project Structure

```
wildfire-cli/
├── src/                    # Source code
│   ├── game/              # Core game logic
│   ├── ui/                # User interface
│   └── scenarios/         # Game content
├── tests/                 # Test files
├── docs/                  # Documentation
├── data/                  # Configuration files
└── .github/               # GitHub automation
```

## Development Workflow

1. **Check Issues** - Browse [open issues](https://github.com/chriswingler/wildfire-cli/issues)
2. **Create Branch** - Feature branches for development
3. **Follow Standards** - See [Code Standards](Code-Standards)
4. **Submit PR** - Use our [PR template](https://github.com/chriswingler/wildfire-cli/blob/main/.github/pull_request_template.md)

## Need Help?

- 📖 **Architecture Details** - See [Architecture Overview](Architecture-Overview)
- 🔧 **Common Issues** - Check [Troubleshooting](Troubleshooting)
- 💬 **Questions** - Start a [Discussion](https://github.com/chriswingler/wildfire-cli/discussions)

---

**Next:** Learn about the [Architecture Overview](Architecture-Overview) or jump into [How to Play](How-to-Play)
```

### 🏗️ Architecture-Overview.md
```markdown
# 🏗️ Architecture Overview

This document explains the technical architecture and design principles of the wildfire-cli project.

## Design Principles

### 🚫 No Visual Fire Grid
**Critical Design Decision**: The game uses internal grid simulation but NEVER displays it visually.

- All fire information communicated through realistic incident reports
- Fire data converted from cellular automata to professional text reports
- Players receive radio-style reports about fire conditions and resource status

### 🎯 Authentic Incident Command
- Game follows real ICS operational period structure (12-24 hour cycles)
- Uses authentic wildfire terminology and radio communication style
- Decisions based on real firefighting tactics and resource deployment
- Educational content teaches actual emergency management principles

### 📝 Text-Only Interface
- Professional terminal UI using Rich library for colors and formatting
- No ASCII art or visual representations of the fire
- Focus on decision-making through text-based situation reports
- Multiple choice tactical decisions with realistic consequences

## Core Components

### 🔥 Fire Simulation Engine (`src/game/fire_grid.py`)
```python
class FireGrid:
    # Internal 6x6 or 8x8 cellular automata grid (never displayed)
    # Terrain types: Forest, Grass, Urban, Ridge, Valley
    # Weather effects: wind direction/speed, humidity, temperature
    # Fire states: Empty, Burning, Burned, Contained
    # Realistic spread rates based on fuel type and conditions
```

### 🚁 Resource Management (`src/game/resources.py`)
```python
class Resource:
    # Hand Crews: 20 firefighters, high mobility, all terrain
    # Helitack: 8 firefighters + helicopter, weather dependent
    # Air Tankers: 2,400 gal retardant, create firebreaks
    # Dozers: Build fire lines, terrain limited
    # Engines: Structure protection, road access required
```

### 🎮 Game Loop (`src/game/game_state.py`)
```python
class GameState:
    # Turn-based operational periods (12-24 hours)
    # ICS planning cycle: briefing → objectives → strategy → allocation → implementation
    # Win/loss conditions based on acres burned, structures saved, safety record
    # Random events: weather changes, equipment failures, spot fires
```

### 🖥️ UI Components (`src/ui/`)
```python
# Rich Panel: Incident reports with color coding
# Rich Table: Resource status and availability
# Rich Prompt: Multiple choice tactical decisions
# Report generation: Convert grid state to authentic text reports
```

## Data Flow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Fire Grid     │    │   Game State     │    │  Report Gen     │
│  (Internal)     │───▶│   Management     │───▶│  (Text Only)    │
│                 │    │                  │    │                 │
│ • Cellular      │    │ • Turn Logic     │    │ • Incident      │
│   Automata      │    │ • Resource       │    │   Reports       │
│ • Weather       │    │   Tracking       │    │ • Status        │
│ • Terrain       │    │ • Win/Loss       │    │   Updates       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Resource      │    │   Decision       │    │   Rich UI       │
│  Deployment     │    │    Engine        │    │  Components     │
│                 │    │                  │    │                 │
│ • Effectiveness │    │ • Multiple       │    │ • Panels        │
│ • Cost Tracking │    │   Choice         │    │ • Tables        │
│ • Availability  │    │ • Consequences   │    │ • Prompts       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Technology Stack

### Core Technologies
- **Python 3.8+** - Main programming language
- **Rich Library** - Terminal UI and formatting
- **Dataclasses** - Clean data structures
- **JSON** - Configuration and scenario storage

### Development Tools
- **pytest** - Testing framework
- **black** - Code formatting
- **flake8** - Style checking
- **mypy** - Type checking
- **GitHub Actions** - CI/CD automation

### Project Management
- **GitHub Issues** - Task tracking with agile labels
- **GitHub Projects** - Sprint planning and kanban boards
- **GitHub Milestones** - Release planning
- **Automated Workflows** - Sprint tracking and metrics

## Educational Architecture

### Learning Progression
1. **Grass Fire** (Simple) - Basic resource deployment
2. **Interface Fire** (Structure Protection) - Priority management
3. **Remote Fire** (Logistics) - Resource accessibility challenges
4. **Campaign Fire** (Multi-day) - Sustained operations planning
5. **Complex Fire** (Multi-agency) - Coordination challenges

### Assessment Integration
- **Decision Consequences** - Realistic outcomes teach cause and effect
- **ICS Terminology** - Authentic vocabulary reinforcement
- **Performance Metrics** - Acres burned, structures saved, cost efficiency
- **Safety Emphasis** - Zero tolerance for firefighter casualties

## Scalability Considerations

### Performance Requirements
- **Fire Simulation**: <100ms per turn progression
- **UI Responsiveness**: Immediate response to user input
- **Memory Usage**: Minimal footprint for accessibility
- **Cross-platform**: Works on Windows, macOS, Linux terminals

### Future Extensibility
- **Scenario System** - JSON-based content expansion
- **Plugin Architecture** - Modular resource types
- **Localization Support** - Multi-language capability
- **Advanced Analytics** - Learning outcome tracking

---

**Next Steps**: Review [Code Standards](Code-Standards) and [Contributing Guide](Contributing-Guide)
```

### 📋 Agile-Process.md
```markdown
# 📋 Agile Development Process

Learn about our agile development methodology, sprint structure, and team collaboration processes.

## Sprint Structure

### 🗓️ Sprint Timeline
- **Duration**: 2 weeks
- **Capacity**: 10-13 story points per sprint
- **Total Project**: 6 sprints (12 weeks)
- **Schedule**: Monday start, Friday end

### 📅 Current Roadmap

| Sprint | Dates | Focus | Milestone |
|--------|-------|-------|-----------|
| **Sprint 1** | Week 1-2 | Foundation & Architecture | v0.1 Planning |
| **Sprint 2** | Week 3-4 | Core Game Mechanics | v0.1 Core Engine |
| **Sprint 3** | Week 5-6 | User Interface | v0.2 UI Polish |
| **Sprint 4** | Week 7-8 | Content & Scenarios | v0.3 Content |
| **Sprint 5** | Week 9-10 | Testing & QA | v1.0 Testing |
| **Sprint 6** | Week 11-12 | Release Preparation | v1.0 Release |

## Epic Organization

### 🔥 Fire Engine Epic (Core Simulation)
- Fire spread simulation engine
- Resource management system
- Weather and terrain modeling

### 🎮 Game Loop Epic (Gameplay Mechanics)
- Operational period structure
- Decision trees and consequences
- Win/loss condition evaluation

### 🖥️ UI/UX Epic (User Interface)
- Rich library components
- Report generation system
- Professional terminal experience

### 📋 Content Epic (Educational Material)
- Scenario system and data
- ICS terminology integration
- Progressive learning objectives

### 🧪 Testing Epic (Quality Assurance)
- Unit and integration testing
- Performance benchmarking
- Educational effectiveness validation

## Sprint Ceremonies

### 🎯 Sprint Planning (Monday Week 1)
**Duration**: 2 hours
**Participants**: Development Team, Product Owner

**Agenda**:
1. Sprint goal definition (15 min)
2. Capacity planning (15 min)
3. Backlog refinement (30 min)
4. Sprint backlog selection (45 min)
5. Task breakdown (15 min)

**Artifacts**:
- Sprint Planning Issue created
- Sprint backlog committed
- Story points allocated

### 📱 Daily Standups (Async)
**Format**: GitHub issue comments
**Frequency**: Daily updates

**Template**:
```markdown
## Daily Standup - [Date]

### Yesterday:
- Completed: [What was accomplished]
- Challenges: [Any blockers or difficulties]

### Today:
- Plan: [What will be worked on]
- Focus: [Priority items]

### Blockers:
- [Any impediments that need resolution]
```

### 🎬 Sprint Review (Friday Week 2)
**Duration**: 1 hour
**Focus**: Demo completed work and gather feedback

**Activities**:
- Sprint summary and achievements
- Working feature demonstrations
- Stakeholder feedback collection
- Next sprint preview

### 🔄 Sprint Retrospective (Friday Week 2)
**Duration**: 1 hour
**Focus**: Process improvement

**Format**:
- What went well ✅
- What could be improved 🔧
- Action items for next sprint 🎯
- Process experiments 🧪

## Issue Management

### 🏷️ Label System
- **Epic Labels**: 🔥 Fire Engine, 🎮 Game Loop, 🖥️ UI/UX, 📋 Content, 🧪 Testing
- **Priority**: 🔴 Critical, 🟠 High, 🟡 Medium, 🟢 Low
- **Status**: ready-for-sprint, in-progress, blocked
- **Type**: user-story, bug, epic, spike

### 📊 Story Point Scale
- **1 point**: Trivial change (< 1 hour)
- **2 points**: Simple task (2-4 hours)
- **3 points**: Standard story (4-8 hours)
- **5 points**: Complex story (1-2 days)
- **8 points**: Large story (3-5 days)
- **13 points**: Epic (needs breakdown)

### ✅ Definition of Done

**Story Level**:
- [ ] All acceptance criteria met
- [ ] Code reviewed and approved
- [ ] Unit tests written and passing (>90% coverage)
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] No new linting errors

**Sprint Level**:
- [ ] All committed stories completed
- [ ] Sprint goal achieved
- [ ] Demo preparation completed
- [ ] Retrospective feedback documented

**Release Level**:
- [ ] All features tested end-to-end
- [ ] Performance benchmarks met
- [ ] Security review completed
- [ ] Documentation complete
- [ ] Release notes prepared

## Automation & Tools

### 🤖 GitHub Actions
- **Auto-labeling** based on issue content
- **Sprint progress tracking** when issues close
- **PR automation** linking to related issues
- **Velocity tracking** and burndown metrics

### 📊 Metrics Tracking
- **Velocity**: Story points completed per sprint
- **Burndown**: Daily progress toward sprint goal
- **Quality**: Bug rates and test coverage
- **Learning**: Educational objective achievement

### 🔄 Continuous Improvement
- Regular process retrospectives
- Workflow automation enhancements
- Tool optimization and integration
- Team feedback incorporation

---

**Related Pages**: [Sprint Ceremonies](Sprint-Ceremonies) | [Contributing Guide](Contributing-Guide) | [Troubleshooting](Troubleshooting)
```

## Manual Wiki Creation Steps

Since GitHub CLI doesn't have direct wiki commands, here's the manual process:

### 1. Create Wiki Pages Manually
1. Go to https://github.com/chriswingler/wildfire-cli/wiki
2. Click "Create the first page"
3. Create "Home" page with the Home.md content above
4. Use "New Page" to create additional pages

### 2. Wiki Page Creation Order
1. **Home** - Main landing page
2. **Getting Started** - Quick setup guide
3. **Architecture Overview** - Technical details
4. **Agile Process** - Development methodology
5. **How to Play** - User instructions (future)
6. **Troubleshooting** - Common issues
7. **Contributing Guide** - Development contribution
8. **FAQ** - Frequently asked questions

### 3. Link Structure
- Use `[[Page-Name]]` syntax for internal wiki links
- Create navigation between related pages
- Maintain consistent formatting and structure

## Benefits of Wiki Implementation

### For Users:
- **Centralized Information** - One place for all documentation
- **Easy Navigation** - Wiki-style linking between pages
- **Search Functionality** - GitHub wiki search
- **Version History** - Track documentation changes

### For Developers:
- **Onboarding** - Clear setup and contribution guides
- **Architecture Reference** - Technical documentation
- **Process Clarity** - Agile methodology documentation
- **Troubleshooting** - Common issue resolution

### For Project Management:
- **Transparency** - Public process documentation
- **Consistency** - Standardized procedures
- **Knowledge Sharing** - Team knowledge preservation
- **Stakeholder Communication** - Clear project information

This wiki structure will provide a comprehensive, professional documentation system that complements our agile development process and makes the project accessible to both users and contributors.
```

### 🔧 Troubleshooting.md
```markdown
# 🔧 Troubleshooting Guide

Common issues and solutions for wildfire-cli development and usage.

## Quick Diagnosis

### 🔍 First Steps
1. **Check Python version**: `python --version` (requires 3.8+)
2. **Verify dependencies**: `pip list | grep rich`
3. **Test basic functionality**: `python src/main.py`
4. **Check repository status**: `git status`

## Development Issues

### GitHub CLI Problems
**Issue**: Permission denied errors
```bash
gh auth status  # Check authentication
gh auth refresh --scopes repo,issues  # Add required scopes
```

**Issue**: Workflow failures
- Check `.github/workflows/` for syntax errors
- Verify permissions in workflow files
- Review workflow logs: `gh run list` and `gh run view RUN_ID`

### Python Environment Issues
**Issue**: Import errors or missing dependencies
```bash
pip install -r requirements.txt  # Install dependencies
pip install --upgrade rich       # Update Rich library
```

**Issue**: Python version compatibility
```bash
python --version  # Check version (need 3.8+)
pyenv install 3.9.7  # Install compatible version if needed
```

## GitHub Actions Workflow Issues

### Common Workflow Errors
**Missing Permissions**:
```yaml
permissions:
  issues: write
  pull-requests: write
  contents: read
```

**Invalid Event Types**:
```yaml
# ❌ Invalid
pull_request:
  types: [opened, merged]

# ✅ Correct  
pull_request:
  types: [opened, closed]
```

**Complex Logic Failures**:
```javascript
// ✅ Add error handling
try {
  await github.rest.issues.create({...});
} catch (error) {
  console.log(`Error: ${error.message}`);
}
```

## Git and Repository Issues

### Branch and Commit Issues
**Issue**: Merge conflicts
```bash
git status                 # Check conflict files
git add .                 # Stage resolved conflicts
git commit -m "Resolve conflicts"
```

**Issue**: Wrong branch
```bash
git branch                # Check current branch
git checkout main         # Switch to main branch
git pull origin main      # Update local main
```

## Development Environment

### Terminal and CLI Issues
**Issue**: Rich library not displaying colors
- Check terminal supports colors: `echo $TERM`
- Update terminal or use compatible terminal emulator
- Force color output: `python -c "from rich.console import Console; Console().print('Test', style='bold red')"`

**Issue**: Path and import problems
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"  # Add src to Python path
python -c "import sys; print(sys.path)"       # Verify Python path
```

## Testing Issues

### pytest Problems
**Issue**: Tests not found
```bash
pytest tests/ -v          # Verbose test discovery
pytest --collect-only     # Show what tests would run
```

**Issue**: Import errors in tests
```bash
pip install -e .          # Install package in development mode
pytest tests/ --tb=short  # Show shorter tracebacks
```

## Project Management Issues

### GitHub Issues and Labels
**Issue**: Labels not found
```bash
gh label list             # Check existing labels
gh label create "name" --color "COLOR" --description "DESC"
```

**Issue**: Milestone assignment
```bash
gh api repos/:owner/:repo/milestones  # List milestones
gh issue edit NUMBER --milestone "MILESTONE_NAME"
```

## Error Reference

### Common Error Patterns

**Python ImportError**:
```
ModuleNotFoundError: No module named 'rich'
```
Solution: `pip install rich`

**Git Permission Error**:
```
Permission denied (publickey)
```
Solution: Set up SSH keys or use HTTPS

**Workflow Syntax Error**:
```
The workflow is not valid. .github/workflows/file.yml: unexpected symbol
```
Solution: Check YAML syntax, especially indentation

**GitHub API Rate Limit**:
```
API rate limit exceeded
```
Solution: Wait for rate limit reset or use authenticated requests

## Getting Help

### Internal Resources
- [Architecture Overview](Architecture-Overview) - Technical details
- [Agile Process](Agile-Process) - Development workflow  
- [Getting Started](Getting-Started) - Setup guide

### External Resources
- [Rich Documentation](https://rich.readthedocs.io/) - Terminal UI library
- [GitHub CLI Manual](https://cli.github.com/manual/) - GitHub CLI reference
- [pytest Documentation](https://docs.pytest.org/) - Testing framework

### Support Channels
- 🐛 **Bug Reports**: [Create Issue](https://github.com/chriswingler/wildfire-cli/issues/new?template=bug_report.yml)
- 💬 **Questions**: [GitHub Discussions](https://github.com/chriswingler/wildfire-cli/discussions)
- 📖 **Documentation**: Check this wiki or repository docs/

---

**Can't find your issue?** [Create a new issue](https://github.com/chriswingler/wildfire-cli/issues/new) with detailed error information.
```