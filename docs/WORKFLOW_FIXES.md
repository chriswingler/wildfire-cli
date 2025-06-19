# 🔧 GitHub Actions Workflow Fixes

This document explains the workflow issues encountered and how they were resolved.

## Issues Identified

### 1. Missing Permissions
**Problem:** GitHub Actions workflows lacked explicit permissions to perform operations.

**Error:**
```
This run likely failed because of a workflow file issue.
```

**Root Cause:** By default, GitHub Actions has minimal permissions. Operations like creating comments, updating issues, or adding labels require explicit permission grants.

**Solution:**
```yaml
permissions:
  issues: write
  pull-requests: write
  contents: read
```

### 2. Complex Conditional Logic
**Problem:** Workflows had complex conditional statements that could fail if context wasn't available.

**Examples:**
- `github.event.action == 'opened' && github.event.issue`
- `github.event.inputs.report_type == 'weekly'`

**Issues:**
- No error handling for missing context
- Complex nested logic without fallbacks
- Assumptions about event structure

**Solution:** Added try-catch blocks and simplified logic:
```yaml
- name: Safe automation
  uses: actions/github-script@v7
  with:
    script: |
      try {
        // Automation logic here
        console.log('Success message');
      } catch (error) {
        console.log(`Error: ${error.message}`);
      }
```

### 3. Invalid Event Types
**Problem:** Some workflows referenced invalid GitHub Actions event types.

**Invalid:**
```yaml
pull_request:
  types: [opened, closed, reopened, merged, ready_for_review]
```

**Issue:** `merged` is not a valid event type for `pull_request` trigger.

**Correct:**
```yaml
pull_request:
  types: [opened, closed, reopened, ready_for_review]
```

**Note:** To detect merged PRs, check `context.payload.pull_request.merged` in the script.

### 4. Overly Complex Initial Implementation
**Problem:** Initial workflows tried to implement too many features at once.

**Issues:**
- Multiple complex jobs in single workflow
- Advanced GraphQL operations
- Complex string parsing and regex
- Assumption of specific issue/PR formats

**Solution:** Created simplified workflow with basic functionality:
- Simple auto-labeling based on title keywords
- Basic sprint progress tracking
- Minimal PR automation
- Comprehensive error handling

## Current Workflow Status

### Active Workflows
- ✅ `simple_automation.yml` - Basic working automation
  - Auto-labels issues based on title keywords
  - Updates sprint progress when issues are closed
  - Simple PR tracking

### Disabled Workflows (for reference)
- 🚫 `project_automation.yml.disabled` - Complex automation (needs fixing)
- 🚫 `agile_metrics.yml.disabled` - Metrics reporting (needs fixing)  
- 🚫 `sprint_planning.yml.disabled` - Sprint automation (needs fixing)

## Fixing Complex Workflows

To re-enable the complex workflows, address these issues:

### 1. Add Error Handling
```javascript
try {
  // Complex logic here
} catch (error) {
  console.log(`Operation failed: ${error.message}`);
  // Don't fail the entire workflow
}
```

### 2. Validate Context Before Use
```javascript
if (!context.payload.issue) {
  console.log('No issue context available');
  return;
}
```

### 3. Simplify Complex Operations
```javascript
// Instead of complex regex parsing
const patterns = [/simple-pattern/g];

// Use simple string operations
if (title.includes('keyword')) {
  // Handle case
}
```

### 4. Test Incrementally
- Start with simple operations
- Add one feature at a time
- Test each addition before proceeding
- Use `workflow_dispatch` for manual testing

## Best Practices for Future Workflows

### 1. Start Simple
```yaml
# Minimal working workflow
name: Test Workflow
on: workflow_dispatch
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Simple test
        run: echo "Workflow works!"
```

### 2. Add Permissions Explicitly
```yaml
permissions:
  issues: write        # For issue operations
  pull-requests: write # For PR operations
  contents: read       # For repository access
```

### 3. Use Error Handling
```javascript
try {
  const result = await github.rest.issues.create({
    owner: context.repo.owner,
    repo: context.repo.repo,
    title: 'Test Issue'
  });
  console.log(`Created issue #${result.data.number}`);
} catch (error) {
  console.log(`Failed to create issue: ${error.message}`);
}
```

### 4. Validate Inputs
```javascript
if (!context.payload.issue) {
  console.log('Issue context not available');
  return;
}

const title = context.payload.issue.title;
if (!title) {
  console.log('Issue title not found');
  return;
}
```

### 5. Use Workflow Dispatch for Testing
```yaml
on:
  workflow_dispatch:    # Manual trigger for testing
  issues:
    types: [opened]     # Automatic trigger
```

## Testing Workflows

### 1. Manual Testing
- Use `workflow_dispatch` trigger
- Test with minimal inputs first
- Check workflow logs for errors

### 2. Event Testing
- Create test issues/PRs
- Monitor workflow execution
- Check for permission errors

### 3. Incremental Deployment
- Enable one job at a time
- Test each job independently
- Add complexity gradually

## Common GitHub Actions Errors

### Permission Denied
```
Error: Resource not accessible by integration
```
**Fix:** Add required permissions to workflow

### Invalid Event Type
```
Invalid event type: merged
```
**Fix:** Use valid event types only

### Context Not Available
```
Cannot read property 'issue' of undefined
```
**Fix:** Validate context before use

### Script Syntax Error
```
Unexpected token
```
**Fix:** Check JavaScript syntax in script blocks

## Recovery Process

1. **Identify failing workflows:** `gh run list`
2. **Check specific failure:** `gh run view RUN_ID`
3. **Fix identified issues** in workflow files
4. **Test with simple case** using `workflow_dispatch`
5. **Gradually re-enable features** once basic functionality works

---

**Last Updated:** June 19, 2025  
**Status:** Simple automation working, complex workflows disabled pending fixes