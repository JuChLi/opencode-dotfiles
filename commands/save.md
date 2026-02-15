---
description: Save current session progress to SESSION.md
---
Save the current session state to SESSION.md for future reference.

## Gather Information

Recent git activity:
!`git log --oneline -10`

Check these files if they exist:
- @AGENTS.md - Project structure
- @SESSION.md - Existing session (to update)

List implementation plans:
!`ls docs/plans/ 2>/dev/null || echo "No plans directory"`

## Write SESSION.md

Create or update `SESSION.md` in the project root with this structure:

```markdown
# Session Summary

> Auto-generated: [current date/time]
> Project: [project name]

## Goal
[What we're trying to accomplish - from conversation context]

## Instructions
[Any specific preferences or constraints discussed]

## Discoveries
[Key findings about the codebase or problem]

## Accomplished
- [Recent meaningful commits with brief descriptions]

## In Progress
- [Current work from conversation context]

## Pending
- [Remaining tasks from plans/ or discussion]

## Relevant Files
- [Key files referenced in this session]
```

## After Writing

1. Show a brief summary of what was saved
2. Ask if the user wants to commit SESSION.md
