# ⚡ Quick GitHub Projects Setup

**TL;DR**: Step-by-step guide to create GitHub Projects for agile development workflow.

## 🎯 Primary Project Setup (5 minutes)

### 1. Create Main Project
- Go to: https://github.com/chriswingler/wildfire-cli/projects
- Click **"New Project"** → **"Team Planning"** template
- **Name**: "Wildfire CLI Development"
- **Description**: "Agile development workspace for sprint planning and execution"

### 2. Add Custom Fields (1 minute each)

**Story Points** (Single Select):
- 1, 2, 3, 5, 8, 13, 21

**Priority** (Single Select):
- 🔴 Critical, 🟠 High, 🟡 Medium, 🟢 Low

**Epic** (Single Select):
- 🔥 Fire Engine, 🎮 Game Loop, 🖥️ UI/UX, 📋 Content, 🧪 Testing

**Sprint** (Iteration):
- 2-week cycles, Monday start

### 3. Add All Issues
- Click **"Add items"** → **"Add from repository"**
- Select all issues (#1-#12)

### 4. Create Views

**Sprint Board** (Board view):
- Group by: Status
- Columns: Todo, In Progress, In Review, Done

**Planning Table** (Table view):
- Group by: Sprint
- Sort by: Priority, Story Points

**Epic Roadmap** (Roadmap view):
- Group by: Epic
- Timeline: 3 months

## 📊 Quick Issue Configuration

Copy-paste these values into each issue's project fields:

```
Issue #1: Story Points=3, Priority=🟠 High, Epic=🧪 Testing, Sprint=Sprint 1
Issue #2: Story Points=2, Priority=🟠 High, Epic=🧪 Testing, Sprint=Sprint 1  
Issue #3: Story Points=8, Priority=🔴 Critical, Epic=🔥 Fire Engine, Sprint=Sprint 1
Issue #4: Story Points=5, Priority=🔴 Critical, Epic=🔥 Fire Engine, Sprint=Sprint 2
Issue #5: Story Points=8, Priority=🔴 Critical, Epic=🎮 Game Loop, Sprint=Sprint 2
Issue #6: Story Points=5, Priority=🟠 High, Epic=🖥️ UI/UX, Sprint=Sprint 3
Issue #7: Story Points=3, Priority=🟡 Medium, Epic=🖥️ UI/UX, Sprint=Sprint 3
Issue #8: Story Points=8, Priority=🟠 High, Epic=📋 Content, Sprint=Sprint 4
Issue #9: Story Points=5, Priority=🟡 Medium, Epic=📋 Content, Sprint=Sprint 4
Issue #10: Story Points=5, Priority=🟡 Medium, Epic=🧪 Testing, Sprint=Sprint 5
Issue #12: Story Points=1, Priority=🟠 High, Epic=🧪 Testing, Sprint=Sprint 1
```

## 🚀 Optional Additional Projects

### Bug Tracker Project
- **Template**: Bug Triage
- **Purpose**: Focused bug resolution workflow
- **Filter**: Issues with "bug" label

### Documentation Hub Project  
- **Template**: Feature Planning
- **Purpose**: Wiki, guides, and educational content
- **Filter**: Issues with "documentation" label

### Release Planning Project
- **Template**: Roadmap
- **Purpose**: Cross-sprint milestone tracking
- **Timeline**: 6-month view with major releases

## ✅ Verification Checklist

After setup, verify:
- [ ] All 12 issues appear in project
- [ ] Story points sum to ~65 total points
- [ ] Sprint 1 has 13 points (Issues #1, #2, #3, #12)
- [ ] Each epic has appropriate issues assigned
- [ ] Kanban board shows logical workflow
- [ ] Roadmap view displays epic timeline

## 🎯 Sprint 1 Ready Status

**Sprint 1 Goal**: Foundation & Core Architecture
**Issues**: #1 (3pts), #2 (2pts), #3 (8pts), #12 (1pt) = 14 points
**Duration**: 2 weeks
**Success Criteria**: Fire simulation working, project structure complete

## 📱 Daily Usage

**Start of Day**: Check Sprint Board view
**During Work**: Move issues between columns
**End of Day**: Update issue status and progress
**Sprint Planning**: Use Planning Table view
**Stakeholder Updates**: Use Epic Roadmap view

---

**Full Setup Guide**: [GitHub Projects Setup](GITHUB_PROJECTS_SETUP.md)
**Agile Process**: [Sprint Ceremonies](SPRINT_CEREMONIES.md)