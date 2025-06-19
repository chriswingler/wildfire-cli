# 🏃 Sprint Ceremonies Guide

This document outlines the agile ceremonies and processes for the Wildfire CLI project development.

## 📅 Sprint Schedule

### Sprint Duration
- **Length**: 2 weeks
- **Start**: Monday
- **End**: Friday (week 2)
- **Capacity**: 10-13 story points per sprint

### Sprint Calendar
| Sprint | Dates | Focus | Milestone |
|--------|-------|-------|-----------|
| Sprint 1 | Week 1-2 | Foundation & Architecture | v0.1 Planning |
| Sprint 2 | Week 3-4 | Core Game Mechanics | v0.1 Core Engine |
| Sprint 3 | Week 5-6 | User Interface | v0.2 UI Polish |
| Sprint 4 | Week 7-8 | Content & Scenarios | v0.3 Content |
| Sprint 5 | Week 9-10 | Testing & QA | v1.0 Testing |
| Sprint 6 | Week 11-12 | Release Preparation | v1.0 Release |

## 🎯 Sprint Planning

### When: Monday Week 1 (Sprint Start)
### Duration: 2 hours
### Participants: Development Team, Product Owner

#### Agenda:
1. **Sprint Goal Definition** (15 min)
   - Define primary objective for the sprint
   - Align with milestone objectives

2. **Capacity Planning** (15 min)
   - Review team velocity from previous sprints
   - Account for holidays, time off, other commitments
   - Set realistic capacity for sprint

3. **Backlog Refinement** (30 min)
   - Review and estimate top priority items
   - Break down large items if needed
   - Clarify acceptance criteria

4. **Sprint Backlog Selection** (45 min)
   - Select items for sprint based on:
     - Priority and business value
     - Team capacity
     - Dependencies and risks
     - Sprint goal alignment

5. **Task Breakdown** (15 min)
   - Break selected items into tasks
   - Identify dependencies and blockers
   - Assign initial ownership

#### Deliverables:
- [ ] Sprint goal defined
- [ ] Sprint backlog committed
- [ ] Sprint planning issue created
- [ ] Tasks assigned and estimated

### Sprint Planning Template:
```markdown
# Sprint X Planning

## Sprint Goal
[Clear, concise statement of what we want to achieve]

## Sprint Capacity
- **Team Velocity**: X story points (based on last 3 sprints)
- **Available Capacity**: Y story points (accounting for time off, etc.)
- **Sprint Duration**: 2 weeks

## Sprint Backlog
- [ ] Issue #X (Y pts) - Brief description
- [ ] Issue #X (Y pts) - Brief description

**Total Committed**: Z story points

## Sprint Risks
- Risk 1: Description and mitigation plan
- Risk 2: Description and mitigation plan

## Definition of Done
- [ ] All acceptance criteria met
- [ ] Code reviewed and approved
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Documentation updated
```

## 📊 Daily Standups

### When: Daily at consistent time
### Duration: 15 minutes max
### Format: Async via GitHub issue comments

#### GitHub Issue Comment Format:
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
- [Requests for help or collaboration]

### Notes:
- [Any additional context or updates]
```

#### Standup Guidelines:
- Focus on progress toward sprint goal
- Identify and escalate blockers quickly
- Keep updates concise and relevant
- Tag team members when collaboration needed

## 🔍 Sprint Review

### When: Friday Week 2 (Sprint End)
### Duration: 1 hour
### Participants: Development Team, Stakeholders

#### Agenda:
1. **Sprint Summary** (10 min)
   - Review sprint goal and achievements
   - Present completed work
   - Demo working features

2. **Sprint Metrics** (10 min)
   - Story points planned vs completed
   - Velocity calculation
   - Burndown chart review

3. **Accomplishments Showcase** (30 min)
   - Demo completed features
   - Show code quality improvements
   - Present test coverage increases

4. **Stakeholder Feedback** (10 min)
   - Gather feedback on completed work
   - Discuss any necessary adjustments
   - Plan follow-up actions

#### Demo Checklist:
- [ ] All completed features demonstrated
- [ ] Code quality metrics presented
- [ ] Test results shown
- [ ] User feedback incorporated
- [ ] Next sprint preview provided

## 🔄 Sprint Retrospective

### When: Friday Week 2 (After Sprint Review)
### Duration: 1 hour
### Participants: Development Team

#### Agenda:
1. **What Went Well** (15 min)
   - Celebrate successes
   - Identify practices to continue

2. **What Could Be Improved** (15 min)
   - Identify pain points
   - Discuss challenges faced

3. **Action Items** (20 min)
   - Define specific improvements
   - Assign ownership and timelines
   - Make commitments for next sprint

4. **Process Improvements** (10 min)
   - Review and adjust team practices
   - Update definition of done if needed
   - Refine estimation process

#### Retrospective Template:
```markdown
# Sprint X Retrospective

## What Went Well ✅
- 
- 
- 

## What Could Be Improved 🔧
- 
- 
- 

## Action Items for Next Sprint 🎯
- [ ] Action item 1 (Owner: @username)
- [ ] Action item 2 (Owner: @username)
- [ ] Action item 3 (Owner: @username)

## Sprint Metrics 📊
- **Planned Points**: X
- **Completed Points**: Y
- **Velocity**: Z points/sprint
- **Completion Rate**: W%

## Process Improvements 🚀
- 
- 
- 

## Experiment for Next Sprint 🧪
[One small process experiment to try]
```

## 📈 Backlog Refinement

### When: Wednesday Week 1 (Mid-sprint)
### Duration: 1 hour
### Participants: Development Team, Product Owner

#### Agenda:
1. **Next Sprint Preparation** (30 min)
   - Review top priority items for next sprint
   - Estimate effort for upcoming stories
   - Break down large epics into stories

2. **Acceptance Criteria Review** (20 min)
   - Clarify requirements for upcoming work
   - Define clear acceptance criteria
   - Identify potential risks or blockers

3. **Dependency Planning** (10 min)
   - Map dependencies between stories
   - Plan integration points
   - Coordinate with external dependencies

#### Refinement Outcomes:
- [ ] Next sprint candidates estimated
- [ ] Acceptance criteria clarified
- [ ] Dependencies identified
- [ ] Risks assessed and mitigated

## 🏆 Definition of Done

### Story Level:
- [ ] All acceptance criteria met
- [ ] Code reviewed and approved by team member
- [ ] Unit tests written and passing (>90% coverage)
- [ ] Integration tests passing
- [ ] Code follows project style guidelines
- [ ] Documentation updated (if applicable)
- [ ] No new linting errors introduced
- [ ] Manual testing completed
- [ ] Performance impact assessed

### Sprint Level:
- [ ] All committed stories completed
- [ ] Sprint goal achieved
- [ ] Demo preparation completed
- [ ] Retrospective feedback documented
- [ ] Next sprint planning prepared

### Release Level:
- [ ] All features tested end-to-end
- [ ] Performance benchmarks met
- [ ] Security review completed
- [ ] Documentation complete and current
- [ ] Release notes prepared
- [ ] Deployment process verified

## 📋 Ceremony Checklist

### Sprint Planning Preparation:
- [ ] Product backlog prioritized
- [ ] User stories estimated
- [ ] Acceptance criteria defined
- [ ] Team capacity calculated
- [ ] Previous sprint velocity reviewed

### Daily Standup Management:
- [ ] Consistent timing maintained
- [ ] Blockers escalated promptly
- [ ] Progress tracked against sprint goal
- [ ] Team collaboration facilitated

### Sprint Review Preparation:
- [ ] Demo environment prepared
- [ ] Completed features tested
- [ ] Metrics and charts updated
- [ ] Stakeholder invitations sent

### Retrospective Follow-through:
- [ ] Action items tracked and completed
- [ ] Process improvements implemented
- [ ] Team feedback incorporated
- [ ] Continuous improvement culture maintained

---

*This guide helps maintain consistent, effective sprint ceremonies that drive continuous improvement and delivery of value.*