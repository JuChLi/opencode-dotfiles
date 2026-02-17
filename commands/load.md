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

Follow these steps.

> **IMPORTANT**: Before executing each step, output a progress message so the user knows what's happening.

### Step 1: Check Progress File

If "Saved Progress" above shows "No saved progress found":
- Inform user and suggest using `/save`
- Stop here

- Output: `[1/6] Checking progress file...` (or `[1/6] No progress found, please use /save first`)

### Step 2: Quick Context Verification

Parse the "5-Question Check" table (if present) to quickly verify context:

| Question | What to Check |
|----------|---------------|
| Where am I? | Current phase/task |
| Where am I going? | Remaining work |
| What's the goal? | North star objective |
| What did I learn? | Key decisions/discoveries |
| What did I do? | Completed work |

This is for YOUR context restoration — no need to read it aloud to user.

- Output: `[2/6] Verifying context...`

### Step 3: Present Summary

Display a **concise** summary optimized for quick context restoration:

- Output: `[3/6] Preparing session summary...`

**Priority Information (Always Show):**
```
## Session Resume

**Last Saved**: [time ago, e.g., "2 days ago (2026-02-14 15:30)"]
**Goal**: [the north star objective]
**Current Task**: [task name] — [status]
**Next Step**: [specific action]
**Blocked By**: [blocker or "None"]

### Phase Progress
[Show phase status table with completion percentage, e.g., "3/5 phases complete (60%)"]
🔴 Incomplete: [list pending/in_progress phases]
✅ Complete: [list complete phases briefly]

### Context for Handoff
[The 2-3 sentence handoff context from progress.md]
```

**Secondary Information (Show Briefly):**
- Work Summary (1-2 sentences max)
- Todo list
- Notes/gotchas

**Critical Context (Show if Present):**
- **Decisions Made**: Remind what choices were made and why (avoid re-discussing)
- **Error Log**: Remind what errors occurred and how they were resolved (avoid repeating)
- **Files Modified**: List relevant files for quick navigation

### Step 4: Compare Current State

Compare current Git status with the recorded state in progress.md:

- Output: `[4/6] Comparing current Git state...`

| Check | Action |
|-------|--------|
| New commits since save | List new commits, note who made them |
| File status changed | Show what's new/modified/deleted |
| State unchanged | Confirm: "State matches last save" |

If commits exist that weren't in "Recent Commits":
- Highlight as "Changes since last save"
- Summarize what changed
- Note if changes affect the "Current Task"

### Step 5: History Summary

If "Progress History" is not empty:
- List last 3 entries only (save time + one-line summary each)
- Most recent first
- No need for full details

- Output: `[5/6] Checking history...` (or `[5/6] No history records`)

### Step 6: Prompt for Action

End with actionable prompt based on phase status and todos:

- Output: `[6/6] Done!` followed by the action prompt

```
### Ready to Continue?

**Suggested Next Step**: [Based on "Next Step" field or first incomplete phase]

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
| Prioritized | Critical info first (goal, task, next step, blockers) |
| Incomplete First | Highlight pending/in_progress phases before complete ones |
| Context-Rich | Show decisions and errors to avoid repetition |
| Actionable | End with clear options |
| Diff-aware | Highlight what changed since last save |

## Edge Cases

| Situation | Action |
|-----------|--------|
| Progress file malformed | Parse what's usable, note issues |
| Old format (no new fields) | Fall back to original parsing, still works |
| Very old progress (>7 days) | Warn that context may be stale |
| No git repo | Skip git comparison steps |
| AGENTS.md has Architecture Decisions | Include relevant decisions |
| AGENTS.md has Gotchas | Remind user of relevant gotchas |

Keep total output under 60 lines for quick scanning.
