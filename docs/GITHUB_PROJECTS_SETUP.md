# 🚀 GitHub Projects Setup Guide

This guide provides step-by-step instructions for creating comprehensive GitHub Projects to manage the wildfire-cli development workflow.

## Why GitHub Projects?

GitHub Projects provides powerful project management capabilities that integrate directly with our repository:
- **Agile Sprint Planning** - Story points, iterations, burndown tracking
- **Kanban Workflows** - Visual task progression and status tracking  
- **Roadmap Visualization** - Timeline view of milestones and releases
- **Custom Fields** - Story points, priority, epic classification
- **Automation** - Automatic issue tracking and status updates
- **Multi-view Support** - Table, Board, and Roadmap perspectives

## Projects to Create

### 1. 🎯 Primary Project: "Wildfire CLI Development"
**Purpose**: Main agile development workspace for sprint planning and execution
**Template**: Team Planning
**Repository**: wildfire-cli

### 2. 📋 Secondary Projects (Optional)
- **🐛 Bug Tracker** - Focused bug triage and resolution
- **📚 Documentation Hub** - Wiki, guides, and educational content
- **🎓 Learning Objectives** - Educational goal tracking and assessment
- **🚀 Release Planning** - Cross-sprint milestone and feature planning

## Step-by-Step Setup

### Project 1: Wildfire CLI Development

#### Step 1: Create the Project
1. Go to: https://github.com/chriswingler/wildfire-cli
2. Click **"Projects"** tab
3. Click **"New Project"** 
4. Choose **"Team Planning"** template
5. Name: **"Wildfire CLI Development"**
6. Description: **"Agile development workspace for wildfire incident commander simulation game"**
7. Click **"Create Project"**

#### Step 2: Configure Custom Fields

**Story Points Field:**
1. Click the **"+"** next to field headers
2. **Field name**: "Story Points"
3. **Field type**: "Single select"
4. **Options**: 
   - 1 (Green)
   - 2 (Blue)  
   - 3 (Yellow)
   - 5 (Orange)
   - 8 (Red)
   - 13 (Purple)
   - 21 (Gray)

**Priority Field:**
1. **Field name**: "Priority"
2. **Field type**: "Single select"
3. **Options**:
   - 🔴 Critical (Red)
   - 🟠 High (Orange)
   - 🟡 Medium (Yellow)
   - 🟢 Low (Green)

**Epic Field:**
1. **Field name**: "Epic"
2. **Field type**: "Single select"
3. **Options**:
   - 🔥 Fire Engine (Red)
   - 🎮 Game Loop (Blue)
   - 🖥️ UI/UX (Green)
   - 📋 Content (Yellow)
   - 🧪 Testing (Purple)

**Sprint Field:**
1. **Field name**: "Sprint"
2. **Field type**: "Iteration"
3. **Duration**: 14 days (2 weeks)
4. **Start day**: Monday
5. **Create iterations**:
   - Sprint 1: Foundation & Architecture
   - Sprint 2: Core Game Mechanics
   - Sprint 3: User Interface
   - Sprint 4: Content & Scenarios  
   - Sprint 5: Testing & QA
   - Sprint 6: Release Preparation

#### Step 3: Add Repository Issues
1. Click **"Add items"** 
2. Select **"Add from repository"**
3. Choose **"wildfire-cli"** repository
4. **Select all issues** (#1-#12)
5. Click **"Add selected items"**

#### Step 4: Configure Issues with Agile Metadata

**🗓️ IMPORTANT: Always Include Dates**
- **Start Date**: When work should begin
- **Target Date**: Expected completion date
- **Epic**: Categorize by functional area
- **Sprint**: Assign to specific iteration

**Issue #1 (Project structure and dependencies)**
- Story Points: 3
- Priority: 🟠 High
- Epic: 🧪 Testing
- Sprint: Sprint 1
- Start Date: 2025-06-20
- Target Date: 2025-07-03

**Issue #2 (Update CLAUDE.md)**
- Story Points: 2  
- Priority: 🟠 High
- Epic: 🧪 Testing
- Sprint: Sprint 1

**Issue #3 (Fire spread simulation engine)**
- Story Points: 8
- Priority: 🔴 Critical
- Epic: 🔥 Fire Engine
- Sprint: Sprint 1

**Issue #4 (Firefighting resource management)**
- Story Points: 5
- Priority: 🔴 Critical
- Epic: 🔥 Fire Engine
- Sprint: Sprint 2

**Issue #5 (Operational period game loop)**
- Story Points: 8
- Priority: 🔴 Critical
- Epic: 🎮 Game Loop
- Sprint: Sprint 2

**Issue #6 (Rich library UI components)**
- Story Points: 5
- Priority: 🟠 High
- Epic: 🖥️ UI/UX
- Sprint: Sprint 3

**Issue #7 (Fire report generation)**
- Story Points: 3
- Priority: 🟡 Medium
- Epic: 🖥️ UI/UX
- Sprint: Sprint 3

**Issue #8 (Scenario system)**
- Story Points: 8
- Priority: 🟠 High
- Epic: 📋 Content
- Sprint: Sprint 4

**Issue #9 (Decision trees and tactical options)**
- Story Points: 5
- Priority: 🟡 Medium
- Epic: 📋 Content
- Sprint: Sprint 4

**Issue #10 (Testing framework)**
- Story Points: 5
- Priority: 🟡 Medium
- Epic: 🧪 Testing
- Sprint: Sprint 5

**Issue #12 (Sprint 1 Planning)**
- Story Points: 1
- Priority: 🟠 High
- Epic: 🧪 Testing
- Sprint: Sprint 1

#### Step 5: Create Project Views

**View 1: Sprint Planning**
1. **View name**: "Sprint Planning"
2. **Layout**: Table
3. **Group by**: Sprint
4. **Sort by**: Priority, Story Points
5. **Filter**: Current sprint iteration
6. **Fields to show**: Title, Assignee, Status, Story Points, Priority, Epic

**View 2: Status Kanban Board**
1. **View name**: "Development Board"
2. **Layout**: Board
3. **Group by**: Status
4. **Columns**:
   - 📥 Backlog
   - 🎯 Ready
   - 🔄 In Progress
   - 🔍 Review
   - ✅ Done
   - 🚀 Deployed
5. **Fields to show**: Story Points, Priority, Epic

**View 3: Priority Kanban Board**
1. **View name**: "Priority Board"
2. **Layout**: Board
3. **Group by**: Priority
4. **Columns** (vertical priority stack):
   - 🔴 Critical
   - 🟠 High
   - 🟡 Medium
   - 🟢 Low
5. **Fields to show**: Status, Story Points, Epic
6. **Sort within columns**: By Status (Ready → In Progress → Review → Done)

**View 4: Epic Roadmap**
1. **View name**: "Epic Roadmap"
2. **Layout**: Roadmap
3. **Group by**: Epic
4. **Timeline**: 3 months
5. **Show**: Sprint boundaries as markers

**View 5: Sprint Burndown**
1. **View name**: "Sprint Metrics"
2. **Layout**: Table
3. **Group by**: Sprint
4. **Show**: Story Points sum, completion status
5. **Filter**: Current and previous sprints

#### Step 6: Configure Automation

**Auto-move to In Progress:**
- **Trigger**: Issue status changes to "In Progress"
- **Action**: Move to "In Progress" column

**Auto-move to Done:**
- **Trigger**: Issue closes
- **Action**: Move to "Done" column

**Sprint Assignment:**
- **Trigger**: Issue labeled with sprint-planning
- **Action**: Set Sprint field to current iteration

#### Step 7: Set Up Project Milestones

Link project to repository milestones:
1. **v0.1 - Core Engine** (Sprint 1-2)
2. **v0.2 - UI Polish** (Sprint 3)
3. **v0.3 - Content** (Sprint 4)
4. **v1.0 - Release** (Sprint 5-6)

## Project Templates Ready to Use

### Template 1: Sprint Planning Meeting
```markdown
# Sprint X Planning

## Sprint Goal
[Define what we want to achieve this sprint]

## Sprint Capacity
- **Team Velocity**: X story points
- **Available Points**: Y story points  
- **Sprint Duration**: 2 weeks

## Sprint Backlog
[Items committed to this sprint - auto-populated from project]

## Sprint Risks
- Risk 1: Description and mitigation
- Risk 2: Description and mitigation

## Definition of Done
- [ ] All acceptance criteria met
- [ ] Code reviewed and approved
- [ ] Unit tests passing (>90% coverage)
- [ ] Integration tests passing
- [ ] Documentation updated
```

### Template 2: Sprint Retrospective
```markdown
# Sprint X Retrospective

## What Went Well ✅
- 
- 

## What Could Be Improved 🔧
- 
- 

## Action Items 🎯
- [ ] Action 1 (Owner: @username)
- [ ] Action 2 (Owner: @username)

## Sprint Metrics 📊
- **Planned Points**: X
- **Completed Points**: Y
- **Velocity**: Z points/sprint
- **Completion Rate**: W%

## Experiment for Next Sprint 🧪
[One process improvement to try]
```

## Advanced Features to Enable

### 1. Insights and Analytics
- **Velocity tracking** across sprints
- **Burndown charts** for sprint progress
- **Cycle time** analysis for issue completion
- **Epic progress** visualization

### 2. Integrations
- **Repository automation** linking issues to project items
- **PR automation** updating project status
- **Milestone tracking** with automatic progress updates
- **Label synchronization** between issues and project

### 3. Reporting
- **Sprint summary reports** with completion metrics
- **Epic progress reports** for stakeholder updates
- **Velocity trends** for capacity planning
- **Quality metrics** tracking bug rates and test coverage

## Benefits of This Setup

### 🎯 For Sprint Planning
- **Visual capacity planning** with story point sums
- **Sprint goal tracking** with clear objectives
- **Velocity measurement** for future planning
- **Risk identification** and mitigation planning

### 📊 For Progress Tracking
- **Real-time burndown** visualization
- **Epic progress** across multiple sprints
- **Blockers identification** and resolution tracking
- **Team performance** metrics and trends

### 🚀 For Stakeholder Communication
- **Professional project views** for external presentation
- **Roadmap visualization** showing future plans
- **Progress transparency** with public project access
- **Milestone tracking** with clear deliverable dates

### 📈 for Continuous Improvement
- **Sprint retrospectives** with data-driven insights
- **Process metrics** for methodology refinement
- **Quality tracking** with defect and test coverage data
- **Team development** with skill and velocity growth

## Maintenance and Updates

### Daily Activities
- **Update issue status** as work progresses
- **Log time and progress** in issue comments
- **Move items** between kanban columns
- **Identify and escalate** blockers

### Weekly Activities  
- **Review sprint progress** against burndown targets
- **Update sprint backlog** with new issues or changes
- **Assess risks** and mitigation strategies
- **Prepare demo content** for sprint review

### Sprint Activities
- **Conduct sprint planning** using project data
- **Run sprint review** with project metrics
- **Perform retrospective** with velocity and quality data
- **Plan next sprint** based on team capacity and velocity

This comprehensive GitHub Projects setup transforms our repository into a full-featured agile development environment that rivals dedicated project management tools while keeping everything integrated with our codebase.

---

**Next Steps:**
1. Create the main "Wildfire CLI Development" project
2. Configure custom fields and views
3. Add all repository issues to the project
4. Set up automation rules
5. Begin Sprint 1 planning and execution

**Resources:**
- [GitHub Projects Documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [Project Management Setup Guide](PROJECT_MANAGEMENT_SETUP.md)
- [Sprint Ceremonies Guide](SPRINT_CEREMONIES.md)