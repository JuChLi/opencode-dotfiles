---
description: Request code review for current changes
---
Dispatch code reviewer to catch issues before they cascade.

## Instructions

Load the `requesting-code-review` skill and request a review.

$ARGUMENTS

## When to Use

**Mandatory:**
- After completing each task
- After implementing major feature
- Before merge to main

**Optional:**
- When stuck (fresh perspective)
- Before refactoring
- After fixing complex bug

## Steps

1. Use the Skill tool to load the `requesting-code-review` skill
2. Get git SHAs (base and head)
3. Dispatch code-reviewer subagent with context
4. Act on feedback:
   - Fix Critical issues immediately
   - Fix Important issues before proceeding
   - Note Minor issues for later
