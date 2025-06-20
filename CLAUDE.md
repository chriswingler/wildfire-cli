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

## Development Workflow

### Claude's Code Management Principles
- Always make sure "no status" tasks are given a status

### Jules Autonomous Coding Agent Integration
- **Context Documentation**: [docs/JULES_CONTEXT.md](docs/JULES_CONTEXT.md) - Complete project understanding for Jules
- **Workflow Guide**: [docs/JULES_WORKFLOW.md](docs/JULES_WORKFLOW.md) - Task management and retriggering process
- **Issue Template**: [docs/JULES_ISSUE_TEMPLATE.md](docs/JULES_ISSUE_TEMPLATE.md) - Quick context for Jules issues
- **Ready Tasks**: 29 issues labeled with `assign-to-jules` for immediate automation

[Rest of the file remains unchanged...]