---
description: Save current session progress to .opencode/progress.md
---
Save the current session state to `.opencode/progress.md` for future reference.

## Gather Information

Recent git activity:
!`git log --oneline -10`

Check these files if they exist:
- @AGENTS.md - Project structure
- @.opencode/progress.md - Existing progress (to archive)

List implementation plans:
!`ls docs/plans/ 2>/dev/null || echo "No plans directory"`

## Setup Directory

Ensure `.opencode/` directory exists in the project root. Create it if missing.

## Setup .gitignore

If this is a Git repository, check if `.gitignore` contains `.opencode/`. If not, append:

```
# OpenCode progress (personal working state)
.opencode/
```

Do NOT overwrite existing content - only append if the rule is missing.

## Archive Old Progress

If `.opencode/progress.md` exists:
1. Read its content
2. Insert the content at the **beginning** of `.opencode/progress-history.md`
3. Add a `---` separator above the archived entry (not needed for the first entry)
4. Newer records should appear at the top of the history file

## Write Progress

Overwrite `.opencode/progress.md` with this structure:

```markdown
# Session Progress

- **Project Path**: [absolute path of working directory]
- **Saved At**: [YYYY-MM-DD HH:mm]

## Recent Commits

[Last 5 commits, format: `hash message`]

## Uncommitted Changes

[List staged / unstaged / untracked files, or "None"]

## Work Summary

[2-5 sentences describing what was done in this session]

## Todo

- [ ] [Remaining or next tasks]

## Notes

[Known bugs, workarounds, or important notes - or "None"]
```

## After Writing

1. Show a brief summary of what was saved
2. If old progress was archived, mention it
3. Confirm that .opencode/ is excluded from git
