# opencode-myquota

Private-use OpenCode plugin that adds a single tool: `myquota`.

It reads OpenCode auth storage (`~/.local/share/opencode/auth.json`) and queries multiple AI platform quota APIs:
- GitHub Copilot
- OpenAI (ChatGPT)
- Z.ai (Zhipu AI)
- MiniMax

Outputs a Taiwan Traditional Chinese quota view with █░ progress bars.

## Install (local dev)

```bash
cd opencode-myquota
npm i
npm run build
# then install the plugin in OpenCode (depends on your OpenCode workflow)
```

## Configure

Ensure your OpenCode `/connect` (or equivalent) writes credentials into `auth.json`:

| Provider | Node Name |
|----------|-----------|
| GitHub Copilot | `github-copilot` |
| OpenAI | `openai` |
| Z.ai | `zai-coding-plan` |
| MiniMax | `minimax-coding-plan` or `minimax` |

## Command

This plugin ships a command file:

- `command/myquota.md`

So you can invoke `/myquota` in OpenCode.
