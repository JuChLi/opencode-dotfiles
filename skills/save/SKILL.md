---
name: save
description: Save current session progress to .opencode/progress.md with structured task tracking, architecture decisions, and handoff context. Use when ending a work session, switching tasks, handing off to another person/session, or wanting to checkpoint progress for later resumption.
---

# Save Session Progress

Save current session state to `.opencode/progress.md` for seamless resumption.

## Workflow

```
Gather Info → Setup Directory → Setup .gitignore → Archive Old Progress → Write Progress → Update AGENTS.md → Confirm
```

## Step 1: Gather Information

Collect context from multiple sources:

```bash
# Recent commits
git log --oneline -10

# Current changes
git status --short

# Existing progress (to archive)
cat .opencode/progress.md 2>/dev/null

# Implementation plans
ls docs/plans/ 2>/dev/null
```

Read if exists:
- `AGENTS.md` — Project structure and guidelines
- `.opencode/progress.md` — Previous progress to archive

## Step 2: Setup Directory

Ensure `.opencode/` directory exists in project root. Create if missing.

## Step 3: Setup .gitignore

If Git repository, check `.gitignore` for `.opencode/`. If missing, append:

```
# OpenCode progress (personal working state)
.opencode/
```

Append only — never overwrite existing content.

## Step 4: Archive Old Progress

If `.opencode/progress.md` exists:

1. Read content
2. Insert at **beginning** of `.opencode/progress-history.md`
3. Add `---` separator above archived entry (skip for first entry)
4. Newer records always at top

## Step 5: Write Progress

Overwrite `.opencode/progress.md` with this structure:

```markdown
# Session Progress

- **Project Path**: [absolute path]
- **Saved At**: [YYYY-MM-DD HH:mm]

## Current Task

- **Task**: [Current task name/description]
- **Status**: [Not Started | In Progress (X%) | Blocked | Completed]
- **Next Step**: [Specific next action to take]
- **Blocked By**: [None | Description of blocker]

## Context for Handoff

[2-3 sentences for next person/session: where you are, what's done, what's next]

## Recent Commits

[Last 5 commits: `hash message`]

## Uncommitted Changes

[Staged/unstaged/untracked files, or "None"]

## Work Summary

[2-5 sentences: what was accomplished this session]

## Todo

- [ ] [Remaining tasks with priority indicators]

## Notes

[Known bugs, workarounds, gotchas, or "None"]
```

### Field Guidelines

| Field | Purpose | Example |
|-------|---------|---------|
| Current Task | What you're working on | "Implement JWT refresh token" |
| Status | Progress indicator | "In Progress (70%)" |
| Next Step | Immediate next action | "Add token expiry validation" |
| Blocked By | What's stopping progress | "Waiting for API spec from backend team" |
| Context for Handoff | Quick orientation | "Auth module 70% done. Login works, refresh token needs expiry check. Start at src/auth/refresh.ts:45" |

## Step 6: Update AGENTS.md (Optional)

If significant decisions were made this session, append to AGENTS.md:

### Architecture Decisions Section

```markdown
## Architecture Decisions

- YYYY-MM-DD: [Decision] — [Reasoning]
```

Only add if:
- New technology choice was made
- Significant design pattern was established
- Important trade-off was decided

### Gotchas Section

```markdown
## Gotchas

- [Issue]: [Workaround]
```

Only add if:
- Non-obvious behavior was discovered
- Workaround was required for a bug/limitation

## Step 7: Confirm

After writing:

1. Show brief summary of what was saved
2. If old progress archived, mention it
3. Confirm `.opencode/` is git-ignored
4. Show the "Context for Handoff" for verification

## Error Handling

| Situation | Action |
|-----------|--------|
| Not a git repo | Skip git-related steps, continue with progress save |
| No changes to save | Still save — record "no changes" state for continuity |
| Write permission error | Report error, suggest checking permissions |
| AGENTS.md doesn't exist | Skip AGENTS.md update step |
