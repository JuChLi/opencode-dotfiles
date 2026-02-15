---
description: 載入專案進度並繼續工作
---
Load the current project's session state from `.opencode/progress.md` and restore working context.

## Saved Progress

!`cat .opencode/progress.md 2>/dev/null || echo "**No saved progress found.** Use /save to save your progress."`

## Progress History

!`cat .opencode/progress-history.md 2>/dev/null || echo "(No history)"`

## Current Git Status

!`git status --short 2>/dev/null || echo "(Not a git repo)"`

## Recent Commits

!`git log --oneline -5 2>/dev/null || echo "(Not a git repo)"`

## Context Sources

Check and read these files if they exist:
- @AGENTS.md - Project overview, architecture decisions, gotchas

Check `docs/plans/` directory for implementation plans:
!`ls docs/plans/ 2>/dev/null || echo "(No plans directory)"`

## Workflow

Follow these steps:

### Step 1: Check Progress File

If "Saved Progress" above shows "No saved progress found":
- Inform user and suggest using `/save`
- Stop here

### Step 2: Present Summary

Display a **concise** summary optimized for quick context restoration:

**Priority Information (Always Show):**
```
## Session Resume

**Last Saved**: [time ago, e.g., "2 days ago (2026-02-14 15:30)"]
**Current Task**: [task name] — [status]
**Next Step**: [specific action]
**Blocked By**: [blocker or "None"]

### Context for Handoff
[The 2-3 sentence handoff context from progress.md]
```

**Secondary Information (Show Briefly):**
- Work Summary (1-2 sentences max)
- Todo list
- Notes/gotchas

### Step 3: Compare Current State

Compare current Git status with the recorded state in progress.md:

| Check | Action |
|-------|--------|
| New commits since save | List new commits, note who made them |
| File status changed | Show what's new/modified/deleted |
| State unchanged | Confirm: "State matches last save" |

If commits exist that weren't in "Recent Commits":
- Highlight as "Changes since last save"
- Summarize what changed
- Note if changes affect the "Current Task"

### Step 4: History Summary

If "Progress History" is not empty:
- List each entry's save time and work summary (one line each)
- Most recent first
- No need for full details

### Step 5: Prompt for Action

End with actionable prompt:

```
### Ready to Continue?

Your pending tasks:
1. [ ] [Most important task]
2. [ ] [Next task]
3. [ ] [Other task]

Which task would you like to work on?
```

If there's a clear "Next Step" defined:
- Suggest starting there
- Ask for confirmation before proceeding

## Presentation Guidelines

| Principle | Implementation |
|-----------|---------------|
| Concise | No verbatim repetition — summarize |
| Prioritized | Critical info first (task, next step, blockers) |
| Actionable | End with clear options |
| Diff-aware | Highlight what changed since last save |

## Edge Cases

| Situation | Action |
|-----------|--------|
| Progress file malformed | Parse what's usable, note issues |
| Very old progress (>7 days) | Warn that context may be stale |
| No git repo | Skip git comparison steps |
| AGENTS.md has Architecture Decisions | Include relevant decisions |
| AGENTS.md has Gotchas | Remind user of relevant gotchas |

Keep total output under 50 lines for quick scanning.
