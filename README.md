# OpenCode Dotfiles

Personal OpenCode configuration with custom commands for session management.

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
| `/load` | Load project progress from SESSION.md and git history |
| `/save` | Save current session progress to SESSION.md |
| `/status` | Alias for `/load` |

### Usage

```bash
# Start of session - load progress
/load

# End of session - save progress
/save
```

## How It Works

These commands implement a "game save/load" pattern for coding sessions:

1. **`/load`** - Reads `SESSION.md`, `AGENTS.md`, `docs/plans/`, and recent git commits to restore context
2. **`/save`** - Analyzes conversation context and git history, then writes a structured summary to `SESSION.md`

This enables seamless context handoff between sessions or when switching between projects.

## Command Syntax

Commands use OpenCode's [custom command features](https://opencode.ai/docs/commands/):

- **Frontmatter** - `description` for TUI display
- **Shell output** - `` !`git log` `` to inject command output
- **File references** - `@SESSION.md` to include file content

## Directory Structure

```
opencode-dotfiles/
├── README.md           # This file
├── install.sh          # Linux/macOS installer
├── install.ps1         # Windows PowerShell installer
└── commands/
    ├── load.md         # /load command
    ├── save.md         # /save command
    └── status.md       # /status command (alias for /load)
```

## Adding New Commands

1. Create a `.md` file in `commands/` directory
2. Add frontmatter with `description`
3. Write the prompt template
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
