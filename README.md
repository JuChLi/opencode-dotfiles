# OpenCode Dotfiles

Personal OpenCode custom commands for session management with structured progress tracking.

## Quick Install

### Option 1: Ask OpenCode

In any OpenCode session, say:

```
請幫我從 https://github.com/JuChLi/opencode-dotfiles clone 並執行安裝腳本
```

### Option 2: Manual Install

```bash
# Clone
git clone https://github.com/JuChLi/opencode-dotfiles.git ~/opencode-dotfiles-temp
cd ~/opencode-dotfiles-temp

# Install (copies commands to ~/.config/opencode/commands/)
./install.sh        # Linux / macOS / Git Bash
.\install.ps1       # Windows PowerShell

# Cleanup
cd ~ && rm -rf ~/opencode-dotfiles-temp
```

## Commands

| Command | Description |
|---------|-------------|
| `/save` | Save session progress with structured task tracking and handoff context |
| `/load` | Load and resume previous progress with state comparison |
| `/find-skills` | Find and install skills from the open agent skills ecosystem |

### Usage

```bash
# Start of session - load progress
/load

# End of session - save progress
/save

# Find skills for a task
/find-skills react testing
```

## How It Works

These commands implement a "game save/load" pattern for coding sessions:

### `/save` captures:

- **Goal** - North star objective for the work session
- **Phase Status** - Multi-step progress tracking (pending/in_progress/complete)
- **Current Task** - What you're working on, status (%), next step, blockers
- **Context for Handoff** - 2-3 sentences for quick orientation
- **Files Modified** - Quick reference for relevant files
- **Decisions Made** - Record WHY you made choices (avoid re-discussing)
- **Error Log** - Track errors and retries (avoid repeating mistakes)
- **Work Summary** - What was accomplished
- **Todo** - Remaining tasks
- **5-Question Check** - Context verification for load
- **Notes** - Gotchas and workarounds
- **Architecture Decisions** - Optional update to AGENTS.md

### `/load` provides:

- **Quick Resume** - Shows goal, task, next step, blockers immediately
- **Phase Progress** - Shows completion percentage (e.g., "3/5 phases = 60%")
- **Context Restoration** - Displays decisions and errors to avoid repetition
- **State Comparison** - Detects changes since last save
- **History Summary** - Previous sessions at a glance (last 3 entries)
- **Actionable Prompt** - Suggests next step and asks for confirmation

## Progress Files

Progress is stored in `.opencode/` directory (auto-added to .gitignore):

```
.opencode/
├── progress.md          # Current session state
└── progress-history.md  # Archived previous sessions
```

### Progress Format

```markdown
# Session Progress

- **Project Path**: /path/to/project
- **Saved At**: 2026-02-16 14:30

## Goal

Implement user authentication with JWT

## Phase Status

| Phase | Status |
|-------|--------|
| 1. Requirements analysis | complete |
| 2. Database design | complete |
| 3. API implementation | in_progress |
| 4. Frontend integration | pending |
| 5. Testing | pending |

## Current Task

- **Task**: Implement JWT refresh token
- **Status**: In Progress (70%)
- **Next Step**: Add token expiry validation
- **Blocked By**: None

## Context for Handoff

Auth module 70% done. Login works, refresh token needs expiry check.
Start at src/auth/refresh.ts:45

## Files Modified

- `src/auth/jwt.ts` — added refresh token logic
- `src/db/users.ts` — added token storage

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Use bcrypt for passwords | Industry standard, secure |
| JWT over sessions | Better for microservices |

## Error Log

| Error | Attempt | Resolution |
|-------|---------|------------|
| TokenExpiredError | 1 | Added expiry check before validation |

## Todo

- [ ] Complete token expiry validation
- [ ] Add unit tests for refresh flow
- [ ] Update API documentation

## 5-Question Check

| Question | Answer |
|----------|--------|
| Where am I? | Phase 3: API implementation |
| Where am I going? | Phase 4-5 |
| What's the goal? | Implement JWT auth |
| What did I learn? | bcrypt + JWT works well |
| What did I do? | Completed DB design, most of API |
```

## DDD Skills

Custom DDD (Domain-Driven Design) skills for AI coding agents.

| Skill | Command | Description |
|-------|---------|-------------|
| **ddd-arch** | `/ddd-arch` | Clean Architecture + DDD + Hexagonal patterns for backend design |
| **ddd-refactor** | `/ddd-refactor` | Safe refactoring using ANALYZE-PRESERVE-IMPROVE cycle |

### Skills Installation

```bash
# Install both skills globally
npx skills add JuChLi/opencode-dotfiles@ddd-arch -g -y
npx skills add JuChLi/opencode-dotfiles@ddd-refactor -g -y
```

### Skills Usage

```bash
# Architecture design
/ddd-arch Create a directory structure for an e-commerce order system

# Refactoring workflow
/ddd-refactor Analyze coupling in src/services/ and create characterization tests
```

### When to Use

| Scenario | Use |
|----------|-----|
| Design new backend projects | `/ddd-arch` |
| Refactor legacy code | `/ddd-refactor` |
| Check architecture violations | `/ddd-arch` |
| Safe code transformation | `/ddd-refactor` |

## Directory Structure

```
opencode-dotfiles/
├── README.md           # This file
├── install.sh          # Linux/macOS installer
├── install.ps1         # Windows PowerShell installer
├── commands/           # OpenCode custom commands
│   ├── save.md         # /save command
│   ├── load.md         # /load command
│   └── find-skills.md  # /find-skills command
└── skills/             # Agent skills
    ├── ddd-arch/       # Clean Architecture + DDD + Hexagonal
    └── ddd-refactor/   # DDD refactoring workflow
```

## Adding New Commands

1. Create a `.md` file in `commands/` directory
2. Add frontmatter with `description`
3. Write the prompt template using:
   - `$ARGUMENTS` - User arguments
   - `` !`command` `` - Shell output injection
   - `@filename` - File content injection
4. Push to GitHub
5. Re-run install script on other machines

Example:

```markdown
---
description: Run tests and fix failures
---
Run the test suite and fix any failing tests.

!`npm test`
```

## Reference

- [OpenCode Commands Documentation](https://opencode.ai/docs/commands/)
- [OpenCode Configuration](https://opencode.ai/docs/config/)
