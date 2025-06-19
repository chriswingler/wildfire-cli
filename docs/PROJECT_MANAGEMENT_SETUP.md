# 🚀 Agile Project Management Setup Guide

This guide sets up the wildfire-cli repository with comprehensive agile project management features using GitHub Projects, sprints, kanban boards, and product management tools.

## Quick Setup Instructions

### 1. Create GitHub Projects Manually
Since GitHub CLI project creation requires additional token scopes, use manual setup:

**🚀 Quick Setup (5 minutes):**
- See: [Quick Projects Setup Guide](QUICK_PROJECTS_SETUP.md)

**📋 Detailed Setup:**
- See: [GitHub Projects Setup Guide](GITHUB_PROJECTS_SETUP.md)

**💡 Additional Projects:**
- See: [Additional Projects Ideas](ADDITIONAL_PROJECTS_IDEAS.md)

### 2. Primary Project: "Wildfire CLI Development"
1. Go to https://github.com/chriswingler/wildfire-cli/projects
2. Click "New Project" → "Team Planning" template
3. Name: "Wildfire CLI Development"
4. Description: "Agile development workspace for sprint planning and execution"
5. Add custom fields: Story Points, Priority, Epic, Sprint
6. Add all repository issues (#1-#12)
7. Configure issue metadata for agile tracking

## Custom Fields Setup

### Story Points Field
```bash
gh api graphql -f query='
mutation {
  createProjectV2Field(input: {
    projectId: "PROJECT_ID"
    dataType: SINGLE_SELECT
    name: "Story Points"
    singleSelectOptions: [
      {name: "1", color: GRAY}
      {name: "2", color: BLUE}
      {name: "3", color: GREEN}
      {name: "5", color: YELLOW}
      {name: "8", color: ORANGE}
      {name: "13", color: RED}
      {name: "21", color: PURPLE}
    ]
  }) {
    projectV2Field {
      id
      name
    }
  }
}'
```

### Priority Field
```bash
gh api graphql -f query='
mutation {
  createProjectV2Field(input: {
    projectId: "PROJECT_ID"
    dataType: SINGLE_SELECT
    name: "Priority"
    singleSelectOptions: [
      {name: "🔴 Critical", color: RED}
      {name: "🟠 High", color: ORANGE}
      {name: "🟡 Medium", color: YELLOW}
      {name: "🟢 Low", color: GREEN}
    ]
  }) {
    projectV2Field {
      id
      name
    }
  }
}'
```

### Epic Field
```bash
gh api graphql -f query='
mutation {
  createProjectV2Field(input: {
    projectId: "PROJECT_ID"
    dataType: SINGLE_SELECT
    name: "Epic"
    singleSelectOptions: [
      {name: "🔥 Fire Engine", color: RED}
      {name: "🎮 Game Loop", color: BLUE}
      {name: "🖥️ UI/UX", color: GREEN}
      {name: "📋 Content", color: YELLOW}
      {name: "🧪 Testing", color: PURPLE}
    ]
  }) {
    projectV2Field {
      id
      name
    }
  }
}'
```

### Sprint Iteration Field
```bash
gh api graphql -f query='
mutation {
  createProjectV2Field(input: {
    projectId: "PROJECT_ID"
    dataType: ITERATION
    name: "Sprint"
    iterationSetting: {
      duration: 14
      startDay: 1
    }
  }) {
    projectV2Field {
      id
      name
    }
  }
}'
```

## Sprint Planning Structure

### Sprint 1: Foundation & Architecture (Weeks 1-2)
**Sprint Goal**: Establish project foundation and core architecture
- **Issues**: #1 (3 pts), #2 (2 pts), #3 (8 pts)
- **Total Points**: 13
- **Focus**: Project setup, documentation, fire simulation engine

### Sprint 2: Core Game Mechanics (Weeks 3-4)
**Sprint Goal**: Implement core game loop and resource management
- **Issues**: #4 (5 pts), #5 (8 pts)
- **Total Points**: 13
- **Focus**: Resource system, operational period gameplay

### Sprint 3: User Interface (Weeks 5-6)
**Sprint Goal**: Professional terminal interface using Rich library
- **Issues**: #6 (5 pts), #7 (3 pts)
- **Total Points**: 8
- **Focus**: UI components, report generation

### Sprint 4: Content & Scenarios (Weeks 7-8)
**Sprint Goal**: Game content and decision-making systems
- **Issues**: #8 (8 pts), #9 (5 pts)
- **Total Points**: 13
- **Focus**: Scenarios, tactical decisions

### Sprint 5: Testing & QA (Weeks 9-10)
**Sprint Goal**: Comprehensive testing and quality assurance
- **Issues**: #10 (5 pts), Bug fixes (3 pts), Polish (2 pts)
- **Total Points**: 10
- **Focus**: Test coverage, bug fixes, performance

### Sprint 6: Release Preparation (Weeks 11-12)
**Sprint Goal**: Documentation, packaging, and release
- **Issues**: Documentation (3 pts), Packaging (2 pts), Release (3 pts)
- **Total Points**: 8
- **Focus**: Release readiness, final polish

## Project Views Setup

### 1. Kanban Board View
**Columns to create:**
- 📥 **Backlog** (status: Todo)
- 🏃 **Sprint Backlog** (status: Todo + current sprint)
- 👷 **In Progress** (status: In Progress)
- 👀 **Code Review** (status: In Progress + has PR)
- 🧪 **Testing** (status: In Progress + testing label)
- ✅ **Done** (status: Done)

### 2. Sprint Planning View
**Filters:**
- Current sprint iteration
- Group by: Epic
- Sort by: Priority, Story Points
- Show: Story Points sum

### 3. Roadmap View
**Configuration:**
- Group by: Milestone
- Show: Epic progress
- Timeline: 3 months
- Markers: Sprint boundaries

### 4. Burnup Chart View
**Metrics:**
- Planned points vs completed points
- Velocity trending
- Sprint capacity vs actual

## Issue Enhancement for Agile

### Current Issues with Agile Metadata

**Issue #1: Project structure and dependencies**
- **Epic**: 🧪 Testing
- **Story Points**: 3
- **Priority**: 🟠 High
- **Sprint**: Sprint 1
- **Acceptance Criteria**:
  - [ ] Python package structure follows best practices
  - [ ] requirements.txt includes all dependencies
  - [ ] Project structure supports modular development
  - [ ] Documentation explains setup process

**Issue #3: Fire spread simulation engine**
- **Epic**: 🔥 Fire Engine
- **Story Points**: 8
- **Priority**: 🔴 Critical
- **Sprint**: Sprint 1
- **Acceptance Criteria**:
  - [ ] Internal grid simulation (no visual display)
  - [ ] Realistic fire spread based on terrain and weather
  - [ ] Cellular automata algorithm implemented
  - [ ] Fire states properly managed
  - [ ] Unit tests cover fire behavior

**Issue #4: Firefighting resource management**
- **Epic**: 🔥 Fire Engine
- **Story Points**: 5
- **Priority**: 🔴 Critical
- **Sprint**: Sprint 2
- **Acceptance Criteria**:
  - [ ] Resource classes for all firefighting assets
  - [ ] Deployment mechanics working
  - [ ] Cost tracking functional
  - [ ] Effectiveness calculations accurate

**Issue #5: Operational period game loop**
- **Epic**: 🎮 Game Loop
- **Story Points**: 8
- **Priority**: 🔴 Critical
- **Sprint**: Sprint 2
- **Acceptance Criteria**:
  - [ ] Turn-based operational periods (12-24 hours)
  - [ ] Game state persistence
  - [ ] Win/loss condition evaluation
  - [ ] Authentic ICS planning cycle

**Issue #6: Rich library UI components**
- **Epic**: 🖥️ UI/UX
- **Story Points**: 5
- **Priority**: 🟠 High
- **Sprint**: Sprint 3
- **Acceptance Criteria**:
  - [ ] Professional incident report panels
  - [ ] Resource status tables
  - [ ] Multiple choice decision menus
  - [ ] Consistent styling throughout

**Issue #7: Fire report generation**
- **Epic**: 🖥️ UI/UX
- **Story Points**: 3
- **Priority**: 🟡 Medium
- **Sprint**: Sprint 3
- **Acceptance Criteria**:
  - [ ] Realistic incident reports from grid state
  - [ ] Multiple report types implemented
  - [ ] Authentic incident command terminology
  - [ ] Professional formatting

**Issue #8: Scenario system**
- **Epic**: 📋 Content
- **Story Points**: 8
- **Priority**: 🟠 High
- **Sprint**: Sprint 4
- **Acceptance Criteria**:
  - [ ] JSON scenario data format
  - [ ] 5 scenarios with progressive difficulty
  - [ ] Scenario loading system
  - [ ] Educational content integration

**Issue #9: Decision trees and tactical options**
- **Epic**: 📋 Content
- **Story Points**: 5
- **Priority**: 🟡 Medium
- **Sprint**: Sprint 4
- **Acceptance Criteria**:
  - [ ] Realistic tactical decisions
  - [ ] Consequence modeling
  - [ ] Multiple valid solution paths
  - [ ] Educational feedback system

**Issue #10: Testing framework**
- **Epic**: 🧪 Testing
- **Story Points**: 5
- **Priority**: 🟡 Medium
- **Sprint**: Sprint 5
- **Acceptance Criteria**:
  - [ ] pytest framework setup
  - [ ] >80% code coverage
  - [ ] Unit and integration tests
  - [ ] CI/CD pipeline integration

## Automation Setup

The automation workflows will be created in the next step to integrate with the project management system.

## Team Velocity Planning

**Target Velocity**: 10-13 story points per 2-week sprint
**Total Project**: ~60 story points across 6 sprints
**Timeline**: 12 weeks (3 months)

This setup transforms GitHub into a comprehensive agile development environment with proper sprint planning, kanban workflows, and product management capabilities.