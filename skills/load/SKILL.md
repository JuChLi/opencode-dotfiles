---
name: load
description: Load project progress from .opencode/progress.md to resume work seamlessly. Use when starting a new session, returning to a project after time away, taking over from another person/session, or needing to understand current project state and pending tasks.
---

# Load Session Progress

Load saved session state from `.opencode/progress.md` and restore working context.

## Workflow

```
Check Progress File → Load Context Sources → Compare Current State → Present Summary → Prompt for Action
```

## Step 1: Check Progress File

```bash
cat .opencode/progress.md 2>/dev/null
```

If no progress file exists:
- Inform user: "No saved progress found"
- Suggest: "Use /save to save your progress"
- Stop here

## Step 2: Load Context Sources

Gather additional context:

```bash
# Current git status
git status --short 2>/dev/null

# Recent commits (for comparison)
git log --oneline -5 2>/dev/null

# Progress history
cat .opencode/progress-history.md 2>/dev/null
```

Read if exists:
- `AGENTS.md` — Project overview, architecture decisions, gotchas
- `docs/plans/` — Implementation plans (list directory)

## Step 3: Compare Current State

Compare current git state with recorded state in `progress.md`:

| Check | Action |
|-------|--------|
| New commits since save | List new commits, note who made them |
| File status changed | Show diff: what's new/modified/deleted |
| State unchanged | Confirm: "State matches last save" |

### Detecting External Changes

If commits exist that weren't in the saved "Recent Commits":
- Highlight these as "Changes since last save"
- Summarize what changed (files, scope)
- Note if changes affect the recorded "Current Task"

## Step 4: Present Summary

Display a **concise** summary optimized for quick context restoration:

### Priority Information (Always Show)

```
## Session Resume

**Last Saved**: [time ago, e.g., "2 days ago (2026-02-14 15:30)"]
**Current Task**: [task name] — [status]
**Next Step**: [specific action]
**Blocked By**: [blocker or "None"]

### Context for Handoff
[The 2-3 sentence handoff context from progress.md]
```

### Secondary Information (Show Briefly)

```
### Work Summary
[Previous session's accomplishments — 1-2 sentences max]

### Todo
- [ ] [Pending items]

### Notes
[Any gotchas or important notes]
```

### State Comparison (If Changes Detected)

```
### Changes Since Last Save
- 3 new commits by @teammate
- Modified: src/auth/refresh.ts, tests/auth.test.ts
- These changes may affect your "Current Task"
```

### History (If Exists, Summarize Only)

```
### Previous Sessions
- 2026-02-14: Implemented login flow
- 2026-02-12: Set up project structure
[One line per session, most recent first]
```

## Step 5: Prompt for Action

End with actionable prompt:

```
### Ready to Continue?

Your pending tasks:
1. [ ] [Most important/blocked task]
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
| AGENTS.md has Architecture Decisions | Include relevant decisions in context |
| AGENTS.md has Gotchas | Remind user of relevant gotchas |

## Output Format

Keep total output under 50 lines for quick scanning. Use collapsible sections or "see more" references for detailed history.
