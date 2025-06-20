# Jules Autonomous Coding Agent - Workflow Guide

This document provides the complete workflow for working effectively with Jules on the Wildfire CLI project.

## 🚀 **Initial Setup for Jules Tasks**

### 1. Issue Preparation
- **Add comprehensive context** from [JULES_CONTEXT.md](JULES_CONTEXT.md)
- **Include specific implementation steps** with file paths and line numbers
- **Apply `assign-to-jules` label** to trigger Jules assignment
- **Add categorization labels** (`jules: testing`, `jules: refactor`, etc.)

### 2. Essential Context Template
```markdown
> **📚 Jules Context**: Read [docs/JULES_CONTEXT.md](../blob/main/docs/JULES_CONTEXT.md) for complete project understanding.

**Project**: Wildfire CLI - Text-based wildfire incident commander simulation game
**Architecture**: Discord bot with async/await, aiosqlite database, no visual grid
**Key Files**: src/discord_wildfire.py (main bot), src/fire_engine.py (simulation)
**Patterns**: Follow existing Discord command and database operation patterns
```

## 🔄 **Jules Task Retriggering (Proven Process)**

### When to Retrigger
- Jules says "waiting for your input"
- Jules asks for "more specific task" 
- Task idle for >30 minutes
- Need to redirect to different approach
- Jules seems stuck on broad requirements

### Step-by-Step Retrigger Process

#### Step 1: Pause Task (Jules Interface)
```
1. Go to Jules web interface (jules.google.com)
2. Find the active task
3. Pause/stop the current task
```

#### Step 2: Label Toggle (GitHub CLI)
```bash
# Remove Jules assignment (triggers system refresh)
gh issue edit [ISSUE_NUMBER] --remove-label "assign-to-jules"

# Wait for system to register the change
sleep 3

# Re-add Jules assignment
gh issue edit [ISSUE_NUMBER] --add-label "assign-to-jules"
```

#### Step 3: Add Specific Guidance Comment
```bash
gh issue comment [ISSUE_NUMBER] --body "**🔄 RETRIGGER REQUEST**

Jules, please implement [SPECIFIC TASK]:

1. **CREATE** [exact file path] with [specific content/pattern]
2. **MODIFY** [specific file:line] to [exact change]
3. **APPLY** [specific pattern from existing code]

**START NOW** with Step 1 - [immediate concrete action].

**Context**: This is for [specific purpose] following patterns in [reference file].
**Priority**: [High/Medium] - [business reason]"
```

#### Step 4: Update Issue Body (Optional)
```bash
gh issue edit [ISSUE_NUMBER] --body "$(gh issue view [ISSUE_NUMBER] --json body | jq -r '.body')

---
## 🚀 **IMMEDIATE ACTION REQUIRED**
**Jules**: Please implement the specific steps outlined in the comments below.
**Priority**: [High/Medium] - [specific need]
**Next Step**: [immediate action required]"
```

## 📋 **Retrigger Templates**

### General Purpose Retrigger
```bash
# Label toggle
gh issue edit 75 --remove-label "assign-to-jules"
sleep 3
gh issue edit 75 --add-label "assign-to-jules"

# Specific guidance
gh issue comment 75 --body "**🔄 RETRIGGER REQUEST**

Jules, please implement [TASK NAME]:

1. **CREATE** src/[module]/[file].py with [specific pattern]
2. **MODIFY** src/[existing_file].py line [number] to add [specific change]
3. **TEST** changes by [specific verification method]

**START NOW** with Step 1 - create the [file] with [pattern].
**Reference**: Follow patterns in src/[example_file].py lines [range]."
```

### Performance Monitoring Retrigger
```bash
gh issue edit 75 --remove-label "assign-to-jules"
sleep 3  
gh issue edit 75 --add-label "assign-to-jules"

gh issue comment 75 --body "Jules, implement performance monitoring:
1. **CREATE** src/utils/performance.py with @time_command decorator
2. **ADD** psutil>=5.9.0 to requirements.txt
3. **APPLY** decorator to Discord commands in discord_wildfire.py lines 1200-1800
**START NOW** with Step 1 - create performance.py file."
```

### Testing Framework Retrigger
```bash
gh issue edit 100 --remove-label "assign-to-jules"
sleep 3
gh issue edit 100 --add-label "assign-to-jules"

gh issue comment 100 --body "Jules, setup testing infrastructure:
1. **ADD** pytest, pytest-asyncio, pytest-cov to requirements.txt
2. **CREATE** tests/ directory with unit/, integration/, fixtures/ subdirs
3. **CREATE** pytest.ini with project configuration
**START NOW** with Step 1 - modify requirements.txt."
```

### Error Handling Retrigger
```bash
gh issue edit 104 --remove-label "assign-to-jules"
sleep 3
gh issue edit 104 --add-label "assign-to-jules"

gh issue comment 104 --body "Jules, fix error handling:
1. **FIND** bare except: clauses in src/discord_wildfire.py lines 129, 1254, 1399, 1506
2. **REPLACE** with specific exception types (discord.Forbidden, aiosqlite.Error)
3. **ADD** logging for each error condition
**START NOW** with line 129 - replace bare except with specific handling."
```

## ✅ **What Makes Retriggers Successful**

### Effective Triggers
- **Label removal/re-addition** - Forces Jules system refresh
- **Specific file paths** - src/exact/file.py with line numbers
- **Concrete implementation steps** - CREATE, MODIFY, ADD, APPLY verbs
- **Example code or patterns** - Reference existing implementations
- **Immediate starting point** - "START NOW with Step 1"
- **Priority indicators** - Business context and urgency

### Ineffective Approaches
- Vague "please continue" requests
- No specific next steps or file locations
- Missing implementation details
- Unclear success criteria
- Too broad or abstract requirements

## 📊 **Success Indicators**

### Jules Successfully Retriggered When:
- **Starts creating files** within 10-15 minutes
- **Follows exact implementation steps** provided
- **Makes specific changes** to designated files/lines
- **Asks implementation questions** (not broad direction requests)
- **Shows measurable progress** on concrete deliverables

### Signs Jules Needs Different Approach:
- Asks for "more specific task" after multiple retriggers
- Keeps requesting broad clarification
- Makes no file changes after 30+ minutes
- Repeatedly asks same type of questions
- **Solution**: Break task into smaller, more atomic steps

## ⚡ **Advanced Retrigger Techniques**

### Multiple Rapid Retriggers (Use Sparingly)
```bash
# For stuck tasks that need strong signal
for i in {1..2}; do
  gh issue edit [#] --remove-label "assign-to-jules"
  sleep 5
  gh issue edit [#] --add-label "assign-to-jules"
  sleep 10
done
```

### Priority Escalation
```bash
# Add urgency labels to signal importance
gh issue edit [#] --add-label "priority: high"
gh issue edit [#] --add-label "good first issue"  # Sometimes helps with task selection
```

### Context Reinforcement
```bash
# Pin important context as first comment
gh issue comment [#] --body "📌 **PINNED CONTEXT**
Jules: This is [specific type] task for [purpose].
Architecture: [key architectural points]
Patterns: Follow [specific examples] in [reference files]
Success: [specific deliverable] created and working."
```

## 🎯 **Best Practices**

### Timing
- **Wait 5-10 minutes** between retrigger attempts
- **Don't retrigger more than 3 times per hour**
- **Give Jules 15-20 minutes** to show progress after retrigger
- **Try different approaches** if multiple retriggers fail

### Communication Style
- **Be specific and concrete** - file paths, line numbers, exact changes
- **Use action verbs** - CREATE, MODIFY, ADD, APPLY, REPLACE
- **Provide examples** - show exact code patterns to follow
- **Set immediate next step** - what to do right now
- **Include business context** - why this matters for the project

### Task Decomposition
- **Break large tasks into 3-5 concrete steps**
- **Each step should be completable in 30-60 minutes**
- **Steps should have measurable deliverables**
- **Later steps can reference earlier step outputs**

## 🔧 **Troubleshooting**

### Jules Won't Start After Retrigger
1. **Check label assignment** - ensure `assign-to-jules` is applied
2. **Verify issue is open** - closed issues won't trigger
3. **Try repository refresh** - may need to re-select repo in Jules interface
4. **Break into smaller task** - current scope may be too large

### Jules Keeps Asking for Direction
1. **Provide more specific file paths** and line numbers
2. **Include exact code examples** to implement
3. **Reference existing patterns** in the codebase
4. **Start with single file creation** rather than multi-file changes

### Multiple Failed Retriggers
1. **Human decomposition needed** - task may be too complex
2. **Create sub-issues** for individual components
3. **Provide more context** about project architecture
4. **Try different Jules-labeled issues** that are more focused

---

*This workflow guide should be referenced whenever working with Jules to ensure effective task completion.*