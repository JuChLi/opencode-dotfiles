---
description: 儲存工作進度到 .opencode/progress.md
---
Save the current session state to `.opencode/progress.md` for seamless resumption.

## Gather Information

Recent git activity:
!`git log --oneline -10 2>/dev/null || echo "(Not a git repo)"`

Current changes:
!`git status --short 2>/dev/null || echo "(Not a git repo)"`

Existing progress (if any):
!`cat .opencode/progress.md 2>/dev/null || echo "(No existing progress)"`

Implementation plans:
!`ls docs/plans/ 2>/dev/null || echo "(No plans directory)"`

Check these files if they exist:
- @AGENTS.md - Project structure and guidelines
- @.opencode/progress.md - Previous progress to archive

## Workflow

Follow these steps in order:

### Step 1: Setup Directory

Ensure `.opencode/` directory exists in project root. Create if missing.

### Step 2: Setup .gitignore

If this is a Git repository, check if `.gitignore` contains `.opencode/`. If not, append:

```
# OpenCode progress (personal working state)
.opencode/
```

Append only — never overwrite existing content.

### Step 3: Archive Old Progress

If `.opencode/progress.md` exists:
1. Read its content
2. Insert at **beginning** of `.opencode/progress-history.md`
3. Add `---` separator above archived entry (skip for first entry)
4. Newer records always at top

### Step 4: Write Progress

Overwrite `.opencode/progress.md` with this structure:

```markdown
# Session Progress

- **Project Path**: [absolute path of working directory]
- **Saved At**: [YYYY-MM-DD HH:mm]

## Goal

[One sentence describing what this work session aims to achieve — your north star]

## Phase Status

<!-- Status: pending / in_progress / complete -->
| Phase | Status |
|-------|--------|
| [Phase 1 description] | [status] |
| [Phase 2 description] | [status] |
| ... | ... |

## Current Task

- **Task**: [Current task name/description]
- **Status**: [Not Started | In Progress (X%) | Blocked | Completed]
- **Next Step**: [Specific next action to take]
- **Blocked By**: [None | Description of blocker]

## Context for Handoff

[2-3 sentences for next person/session: where you are, what's done, what's next]

## Files Modified

<!-- Quick reference for load to locate relevant files -->
- `[file path]` — [brief description of changes]
- ...

## Decisions Made

<!-- Remember WHY you made choices, or "None" -->
| Decision | Rationale |
|----------|-----------|
| [decision] | [reasoning] |

## Error Log

<!-- Track errors and retries to avoid repeating mistakes, or "None" -->
| Error | Attempt | Resolution |
|-------|---------|------------|
| [error description] | [attempt #] | [how it was resolved] |

## Git Status

### Recent Commits

[Last 5 commits: `hash message`]

### Uncommitted Changes

[Staged/unstaged/untracked files, or "None"]

## Work Summary

[2-5 sentences: what was accomplished this session]

## Todo

- [ ] [Remaining tasks with priority indicators]

## 5-Question Check

<!-- Quick context verification for load -->
| Question | Answer |
|----------|--------|
| Where am I? | [Current phase/task] |
| Where am I going? | [Remaining phases] |
| What's the goal? | [Restate the goal] |
| What did I learn? | [Key discoveries or decisions] |
| What did I do? | [Brief summary of completed work] |

## Notes

[Known bugs, workarounds, gotchas, or "None"]
```

### Field Guidelines

| Field | Purpose | Example |
|-------|---------|---------|
| Goal | North star for this work | "Implement user authentication with JWT" |
| Phase Status | Track multi-step progress | "Phase 2: in_progress" |
| Current Task | What you're working on | "Implement JWT refresh token" |
| Status | Progress indicator | "In Progress (70%)" |
| Next Step | Immediate next action | "Add token expiry validation" |
| Blocked By | What's stopping progress | "Waiting for API spec" |
| Context for Handoff | Quick orientation | "Auth 70% done. Login works, need expiry check. Start at src/auth/refresh.ts:45" |
| Files Modified | Quick file reference | "`src/auth/jwt.ts` — added refresh logic" |
| Decisions Made | Remember the WHY | "Used bcrypt — industry standard" |
| Error Log | Avoid repeating mistakes | "NullPointer at line 45 — added null check" |
| 5-Question Check | Context verification | Answers all 5 reboot questions |

### Step 5: Update AGENTS.md (Optional)

If significant decisions were made, append to AGENTS.md:

**Architecture Decisions** (only if new tech choice or design pattern):
```markdown
## Architecture Decisions

- YYYY-MM-DD: [Decision] — [Reasoning]
```

**Gotchas** (only if non-obvious behavior discovered):
```markdown
## Gotchas

- [Issue]: [Workaround]
```

### Step 6: Git Operations

If this is a Git repository with uncommitted changes:

1. **Stage all changes**: `git add -A`
2. **Commit**: Use a descriptive message based on work summary (e.g., `chore: save progress - [brief description]`)
3. **Push**: `git push`
4. **Verify**: Run `git status` to confirm working tree is clean

If no uncommitted changes, skip this step.

### Step 7: Confirm

After writing:
1. Show brief summary of what was saved
2. If old progress was archived, mention it
3. Confirm `.opencode/` is git-ignored
4. Show git status (branch, sync status)
5. Show the "Context for Handoff" for verification
