---
description: Load project progress (like loading a game save)
---
Load the current project's session state and provide a progress summary.

## Saved Progress

!`cat .opencode/progress.md 2>/dev/null || echo "**No saved progress found.** Use /save to save your progress."`

## Progress History

!`cat .opencode/progress-history.md 2>/dev/null || echo "(No history)"`

## Current Git Status

!`git status --short 2>/dev/null || echo "(Not a Git project)"`

## Context Sources

Check and read these files if they exist:
- @AGENTS.md - Project overview and guidelines

Check `docs/plans/` directory for implementation plans.

## Steps

1. **Check progress file**: If "Saved Progress" above shows no record, inform user and suggest using `/save`, then stop.
2. **Present latest progress**: From the loaded `progress.md`, summarize:
   - Last saved time
   - Work summary
   - Todo list
   - Notes
3. **Compare current state**: Compare current Git status with the recorded "Uncommitted Changes" and "Recent Commits":
   - If there are new commits → notify user
   - If file status changed → list differences
   - If unchanged → confirm state matches last save
4. **History summary**: If "Progress History" is not empty, briefly list each entry's save time and work summary (one line each, no details).
5. **Ask user**: Show the todo list and ask which item to continue working on.

## Notes

- Keep it concise - help user quickly resume work, no need to repeat everything verbatim.
- If progress file format is unusual, parse and present whatever is usable.
