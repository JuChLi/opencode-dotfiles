---
description: Check project status (alias for /load)
---
Load the current project's session state and provide a progress summary.

## Context Sources

Check and read these files if they exist:
- @AGENTS.md - Project overview and guidelines
- @SESSION.md - Previous session summary
- @.opencode/SESSION.md - Alternative session location

Check `docs/plans/` directory for implementation plans.

## Git History

Recent commits:
!`git log --oneline -5`

## Output Format

Summarize the project state:

```
Project: [name from directory or AGENTS.md]
Location: [current working directory]

Recent Activity:
- [summarize from git log]

In Progress / Pending:
- [from SESSION.md or plans/]

Suggested Next Steps:
- [actionable recommendations]
```

If no SESSION.md exists, suggest creating one with `/save`.
