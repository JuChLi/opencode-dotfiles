# opencode-minimax

Private-use OpenCode plugin that adds a single tool: `myminimax`.

It reads OpenCode auth storage (`~/.local/share/opencode/auth.json`) and queries MiniMax Coding Plan remains API, then prints a Taiwan Traditional Chinese quota view with █░ progress bars.

## Install (local dev)

```bash
npm i
npm run build
# then install the plugin in OpenCode (depends on your OpenCode workflow)
```

## Configure

Ensure your OpenCode `/connect` (or equivalent) writes MiniMax credentials into `auth.json` under either:

- `minimax-coding-plan`
- `minimax`

Supported fields inside the node:

- `key` / `api_key` / `token` (API Key)
- `groupId` / `GroupId` / `group_id` / `groupID` (optional GroupId)

## Command

This plugin also ships a command file:

- `command/myminimax.md`

So you can invoke `/myminimax` in OpenCode.
