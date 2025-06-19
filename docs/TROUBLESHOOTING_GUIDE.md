# 🔧 Troubleshooting Guide

This document captures common errors encountered during project setup and their solutions to prevent future issues.

## GitHub CLI and Project Management Issues

### 1. GitHub Project Creation Permission Errors

**Error:**
```bash
gh project create --title "Wildfire CLI Development"
# Error: owner is required when not running interactively

gh project create --title "Wildfire CLI Development" --owner "@me"
# Error: your authentication token is missing required scopes [project read:project]
```

**Root Cause:**
- GitHub CLI requires explicit owner specification in non-interactive mode
- Default GitHub CLI token lacks `project` and `read:project` scopes required for GitHub Projects

**Solution:**
```bash
# Method 1: Use GraphQL API directly (if you have project scopes)
gh api graphql -f query='
mutation {
  createProjectV2(input: {
    ownerId: "USER_ID"
    title: "Project Name"
  }) {
    projectV2 {
      id
      number
      title
      url
    }
  }
}'

# Method 2: Manual creation (recommended)
# 1. Go to GitHub repository → Projects tab
# 2. Click "New Project" → Choose template
# 3. Configure custom fields via UI
```

**Prevention:**
- Document that GitHub Projects require manual creation or token scope expansion
- Provide clear instructions for manual setup as fallback
- Include auth refresh commands in setup documentation

### 2. GitHub CLI Authentication Scope Issues

**Error:**
```bash
gh auth refresh -s project,read:project
# Error: --hostname required when not running interactively

gh auth refresh -s project,read:project --hostname github.com
# Error: Command timed out after 2m 0.0s 
# ! First copy your one-time code: 1718-F0D2
# Open this URL to continue in your web browser: https://github.com/login/device
```

**Root Cause:**
- GitHub CLI authentication requires interactive browser flow for scope changes
- Non-interactive environments cannot complete OAuth device flow

**Solution:**
```bash
# Check current scopes
gh auth status

# For non-interactive environments, use GraphQL API within existing scopes
# Or document manual token creation process
```

**Prevention:**
- Always check existing token scopes before attempting project operations
- Provide alternative workflows that work with standard repo scopes
- Document manual token configuration for advanced features

### 3. GitHub CLI Milestone Creation Command Not Found

**Error:**
```bash
gh milestone create "v0.1 - Core Engine"
# Error: unknown command "milestone" for "gh"
```

**Root Cause:**
- GitHub CLI doesn't have direct milestone commands
- Milestones must be created via REST API

**Solution:**
```bash
# Use GitHub REST API instead
gh api repos/:owner/:repo/milestones -X POST \
  -f title="v0.1 - Core Engine" \
  -f description="Basic game mechanics and simulation"
```

**Prevention:**
- Use `gh api` commands for features not available in CLI
- Document API alternatives for missing CLI commands
- Check GitHub CLI documentation for supported commands

### 4. Label Not Found Errors During Issue Management

**Error:**
```bash
gh issue edit 1 --add-label "ready-for-sprint"
# Error: failed to update: 'ready-for-sprint' not found

gh issue create --label "sprint-planning,planning"
# Error: could not add label: 'sprint-planning' not found
```

**Root Cause:**
- Custom labels must be created before they can be used
- Issue creation fails if any specified label doesn't exist

**Solution:**
```bash
# Create labels first
gh label create "ready-for-sprint" --color "0E8A16" --description "Issue is ready for sprint planning"
gh label create "sprint-planning" --color "B60205" --description "Sprint planning and coordination"

# Then use in issues
gh issue edit 1 --add-label "ready-for-sprint"
```

**Prevention:**
- Create all custom labels immediately after repository setup
- Document required labels in setup instructions
- Consider using label configuration files

### 5. Issue Template Body Parameter Not Supported

**Error:**
```bash
gh project create --title "Wildfire CLI Development" --body "Description text"
# Error: unknown flag: --body
```

**Root Cause:**
- GitHub CLI project create command doesn't support `--body` parameter
- Only `--title` and `--owner` are supported

**Solution:**
```bash
# Use only supported parameters
gh project create --title "Wildfire CLI Development" --owner "@me"

# Or use GraphQL API for full control
gh api graphql -f query='mutation { createProjectV2(input: {...}) {...} }'
```

**Prevention:**
- Check GitHub CLI help for supported parameters: `gh project create --help`
- Use GraphQL API for advanced configuration options
- Test commands with minimal parameters first

## Git and Repository Issues

### 6. Git Default Branch Naming

**Error:**
```bash
git init
# hint: Using 'master' as the name for the initial branch
# hint: Names commonly chosen instead of 'master' are 'main'
```

**Root Cause:**
- Git defaults to 'master' branch name
- GitHub repositories typically use 'main' as default

**Solution:**
```bash
# Rename branch immediately after init
git init
git branch -m main

# Or configure Git globally
git config --global init.defaultBranch main
```

**Prevention:**
- Set global Git configuration for consistent branch naming
- Include branch rename in setup scripts
- Document expected branch structure

### 7. File Permission and Access Issues

**Error:**
```bash
gh repo view --web
# Error: /usr/bin/xdg-open: 882: x-www-browser: Permission denied
# Multiple browser permission errors...
```

**Root Cause:**
- WSL/Linux environment lacks browser access
- xdg-open cannot find available browser

**Solution:**
```bash
# Get repository URL without opening browser
gh repo view --json url --jq '.url'

# Or use specific browser if available
export BROWSER=wslview  # For WSL
```

**Prevention:**
- Test environment capabilities before using browser-dependent commands
- Provide alternative commands for headless environments
- Document environment-specific considerations

## Automation and Workflow Issues

### 8. GitHub Actions Token Scope Limitations

**Error in Workflow:**
```yaml
# This will fail if token lacks project scopes
- name: Create Project via API
  run: gh api graphql -f query='mutation { createProjectV2(...) }'
```

**Root Cause:**
- GitHub Actions GITHUB_TOKEN has limited default scopes
- Project management requires additional permissions

**Solution:**
```yaml
# Use available scopes only, or document manual steps
- name: Create Project Items
  run: |
    # Use repository-scoped operations instead
    gh issue create --title "Project Setup"
    
# Or use personal access token with proper scopes
- name: Project Management
  env:
    GH_TOKEN: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
  run: gh api graphql -f query='...'
```

**Prevention:**
- Document required token scopes for each automation
- Provide fallback workflows for limited environments
- Test automations with default GitHub Actions permissions

### 9. JSON Parsing and JQ Expression Errors

**Error:**
```bash
gh api repos/:owner/:repo/milestones --jq '.[] | {number, title, description}'
# Error: failed to parse jq expression (line 1, column 8)
```

**Root Cause:**
- Complex jq expressions with object construction syntax
- GitHub CLI jq parsing limitations

**Solution:**
```bash
# Use simpler jq expressions
gh api repos/chriswingler/wildfire-cli/milestones | jq '.[] | "\(.number): \(.title) - \(.description)"'

# Or process with multiple simpler commands
gh api repos/:owner/:repo/milestones | jq '.[].title'
```

**Prevention:**
- Test jq expressions incrementally
- Use string interpolation instead of object construction
- Validate JSON structure before complex queries

## Development Environment Setup

### 10. Python Project Structure Best Practices

**Issue:** Ensuring clean, maintainable project structure from start

**Solution Applied:**
```
wildfire-cli/
├── src/                   # Source code (not root level)
│   ├── game/             # Core game logic
│   ├── ui/               # User interface
│   └── scenarios/        # Game content
├── tests/                # Test files
├── docs/                 # Documentation
├── data/                 # Configuration files
└── .github/              # GitHub automation
```

**Benefits:**
- Separates source from configuration
- Supports proper Python packaging
- Clear module organization
- Testable architecture

**Prevention:**
- Follow established Python project templates
- Document architectural decisions
- Use consistent naming conventions

## Process and Planning Lessons

### 11. Agile Setup Complexity Management

**Challenge:** Implementing comprehensive agile features without overwhelming complexity

**Solution:**
- Start with core features (issues, labels, milestones)
- Add automation incrementally
- Provide both automated and manual workflows
- Document everything for future reference

**Key Principles:**
- Fail gracefully with clear error messages
- Provide multiple solution paths
- Test in constrained environments first
- Document troubleshooting steps immediately

### 12. Token and Permission Management

**Best Practices Learned:**
- Always check current permissions before attempting operations
- Provide clear instructions for manual alternatives
- Document required scopes for each feature
- Test with minimal permissions first

**Security Considerations:**
- Never store tokens in repository
- Use environment variables for sensitive data
- Provide scope-minimal solutions
- Document permission requirements clearly

## GitHub Actions Workflow Issues

### 13. Workflow File Syntax and Permission Errors

**Error:**
```bash
gh run list
# Shows: completed failure (0s duration)

gh run view RUN_ID
# Error: This run likely failed because of a workflow file issue
```

**Root Cause:**
- Missing permissions in workflow files
- Invalid event types in triggers
- Complex conditional logic without error handling
- YAML syntax errors

**Solution:**
```yaml
# Add explicit permissions
permissions:
  issues: write
  pull-requests: write
  contents: read

# Use valid event types only
on:
  pull_request:
    types: [opened, closed, ready_for_review]  # Not 'merged'

# Add error handling in scripts
- uses: actions/github-script@v7
  with:
    script: |
      try {
        // Automation logic
      } catch (error) {
        console.log(`Error: ${error.message}`);
      }
```

**Prevention:**
- Start with simple workflows and add complexity incrementally
- Test workflows with `workflow_dispatch` trigger first
- Add explicit permissions for all required operations
- Use comprehensive error handling in scripts
- Validate GitHub Actions syntax before committing

### 14. Overly Complex Initial Automation

**Issue:** Implementing comprehensive automation features before establishing basic functionality

**Problems:**
- Complex conditional logic fails without proper context
- Multiple failure points in single workflow
- Assumptions about event structure and data availability
- No fallback for missing context or permissions

**Solution:**
- Create minimal working workflow first
- Add features one at a time
- Test each addition before proceeding
- Provide graceful degradation for missing features
- Use simple string operations instead of complex regex

**Example Simple Workflow:**
```yaml
name: Basic Automation
on:
  issues:
    types: [opened]
permissions:
  issues: write
jobs:
  simple_task:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/github-script@v7
        with:
          script: |
            console.log('Workflow executed successfully');
```

**Prevention:**
- Follow incremental development approach
- Test workflows in isolation
- Document each automation feature separately
- Provide manual alternatives for complex automation

## Quick Reference: Common Commands

### Check GitHub CLI Status
```bash
gh auth status                    # Check authentication and scopes
gh repo view                     # Verify repository access
gh issue list                    # Test basic issue access
gh api user                      # Check API access
```

### Create Labels (Safe Order)
```bash
gh label create "label-name" --color "COLOR" --description "Description"
gh label list                   # Verify creation
```

### Troubleshoot API Access
```bash
gh api repos/:owner/:repo       # Test basic repo API
gh api graphql -f query='{viewer{login}}'  # Test GraphQL access
```

### Check Project Capabilities
```bash
gh api repos/:owner/:repo/projects  # List existing projects (if any)
gh api user/projects            # List user projects
```

---

## 🔄 Continuous Improvement

This document should be updated whenever new errors are encountered. Each error entry should include:

1. **Exact error message** (copy-paste)
2. **Root cause analysis** (why it happened)
3. **Working solution** (tested fix)
4. **Prevention strategy** (how to avoid)

**Last Updated:** June 19, 2025
**Next Review:** After Sprint 1 completion

---

*Remember: Good documentation of errors saves hours of debugging later. Always capture the full error context and working solutions.*