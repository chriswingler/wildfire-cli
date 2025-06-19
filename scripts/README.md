# GitHub Project Setup Scripts

**Programmatic creation of GitHub project boards for wildfire-cli kanban workflow.**

## 🎯 **Purpose**

These scripts automate the creation of GitHub project boards with:
- Kanban workflow views (Todo → In Progress → Review → Done)
- Sprint planning views (Current → Next → Future)
- Work stream views (UI/UX → Game Engine → Content → Infrastructure)
- All existing issues automatically added and categorized

## 🔧 **Option 1: GitHub CLI Script (Recommended)**

### **Prerequisites**
GitHub CLI needs `project` and `read:project` scopes:

```bash
# Check current scopes
gh auth status

# Refresh with project scopes (requires browser authentication)
gh auth refresh -s project,read:project --hostname github.com

# Verify new scopes
gh auth status
```

### **Run Script**
```bash
# Make executable
chmod +x scripts/create_github_project.sh

# Run project creation
./scripts/create_github_project.sh
```

### **Expected Output**
```
🚀 Creating GitHub Project for Wildfire CLI...
📋 Repository Owner ID: MDQ6VXNlcjM1NDAzNjQx
✅ Project Created!
   Project ID: PVT_kwDOO-HhX84AyBAU
   Project Number: 1
   Project URL: https://github.com/users/chriswingler/projects/1
🔗 Repository linked to project
📊 Project fields retrieved
🔧 Creating custom fields...
✅ Custom fields created
📝 Adding existing issues to project...
  Adding Issue #22: Discord Interactive Interface
  Adding Issue #23: Rookie Commander Tutorial
  Adding Issue #24: Real-time Game Feel
  [... all issues ...]
✅ All issues added to project
🔍 Creating project views...
✅ Project views created

🎉 GitHub Project setup complete!
   Access your project at: https://github.com/users/chriswingler/projects/1
```

## 🤖 **Option 2: GitHub Actions Workflow**

### **Setup Personal Access Token**
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with scopes: `repo`, `project`, `read:project`
3. Add token as repository secret: `PROJECT_MANAGEMENT_TOKEN`

### **Run Workflow**
1. Go to repository → Actions → "Setup GitHub Project Board"
2. Click "Run workflow"
3. Set "Create new GitHub project board" to `true`
4. Click "Run workflow"

## 📋 **What Gets Created**

### **Project Structure**
- **Project Name:** Wildfire CLI Development
- **Description:** Sprint planning and kanban workflow for wildfire-cli development
- **Repository:** Automatically linked to wildfire-cli repo

### **Custom Fields**
- **Story Points:** Number field for velocity tracking
- **Sprint:** Select field (Sprint 4, Sprint 5, Future)

### **Project Views**
1. **Kanban Workflow** - Group by Status labels
   - Todo (`status: todo`)
   - In Progress (`status: in-progress`) 
   - Review (`status: review`)
   - Done (`status: done`)

2. **Sprint Planning** - Group by Iteration labels
   - Current (`iteration: current`)
   - Next (`iteration: next`)
   - Future (`iteration: future`)

3. **Work Streams** - Group by Area labels
   - UI/UX (`area: ui-ux`)
   - Game Engine (`area: game-engine`)
   - Content (`area: content`)
   - Infrastructure (`area: infrastructure`)

### **Issues Added**
All existing repository issues automatically added:

**Sprint 4 (Current):**
- Issue #22: Discord Interactive Interface (6 pts)
- Issue #23: Rookie Commander Tutorial (6 pts)
- Issue #24: Real-time Game Feel (6 pts)

**Sprint 5 (Next):**
- Issue #20: Epic Enhanced Multiplayer Experience
- Issue #4: Discord firefighting resource management
- Issue #5: Discord operational period game loop

**Future Planning:**
- Issue #8: Scenario system and initial scenarios
- Issue #9: Decision trees and tactical options
- Issue #10: Testing framework and core tests

**Completed:**
- Issue #25: GitHub Project Setup (done)
- Issue #6: Discord UI components (done)
- Issue #2: CLAUDE.md updates (done)

## 🔍 **Manual Configuration (After Script)**

### **View Configuration**
The script creates views but you may need to configure grouping:

1. **Go to project board**
2. **For each view:**
   - Click view name dropdown
   - Select "Group by"
   - Choose appropriate field:
     - Kanban Workflow → Group by "Labels" → Filter for `status:`
     - Sprint Planning → Group by "Labels" → Filter for `iteration:`
     - Work Streams → Group by "Labels" → Filter for `area:`

### **Add Story Points**
For Sprint 4 issues, add story point values:
- Issue #22: 6 points
- Issue #23: 6 points  
- Issue #24: 6 points

### **Set Up Automation**
Configure automatic status updates:
- When PR opened → Move to "In Progress"
- When PR merged → Move to "Done"
- When issue closed → Move to "Done"

## 🛠️ **Troubleshooting**

### **Permission Errors**
```bash
# Error: your authentication token is missing required scopes [read:project]
gh auth refresh -s project,read:project --hostname github.com
```

### **GraphQL Errors**
```bash
# Check API access
gh api graphql -f query='{ viewer { login } }'

# Verify repository access
gh api repos/chriswingler/wildfire-cli
```

### **Script Execution Errors**
```bash
# Make script executable
chmod +x scripts/create_github_project.sh

# Check script syntax
bash -n scripts/create_github_project.sh
```

## 📊 **Integration with Existing Workflow**

### **GitHub CLI Commands Still Work**
```bash
# Move issues through kanban workflow
gh issue edit 22 --remove-label "status: todo" --add-label "status: in-progress"

# Sprint planning moves
gh issue edit 25 --add-label "iteration: next" --milestone "Sprint 5"

# Work stream categorization
gh issue edit 27 --add-label "area: game-engine"
```

### **Wiki Documentation References**
- [Kanban Workflow](../wiki/Kanban-Workflow.md) - Complete workflow documentation
- [Sprint Planning](../wiki/Sprint-Planning.md) - PM processes and ceremonies
- [Velocity Analysis](../wiki/Velocity-Analysis.md) - Sprint metrics and capacity planning

---

**These scripts provide full automation of GitHub project board creation with integration to existing kanban workflow and sprint planning processes.**