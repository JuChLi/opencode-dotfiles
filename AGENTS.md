# OpenCode Dotfiles

## 重要原則

- **不要去 `.claude/` 找東西**：除非使用者特別註明，否則不應該讀取或修改 `~/.claude/` 目錄下的任何檔案。那是給 Claude Code 用的，與 OpenCode 無關。

## OpenCode 目錄結構

| 目錄 | 用途 |
|------|------|
| `~/.config/opencode/` | OpenCode 設定檔（`opencode.json`、`commands/`） |
| `~/.agents/skills/` | Skills 存放處（AI 自動觸發） |

## 此 Repo 的用途

管理自訂的 commands 和 skills，透過 symlink 連結到 OpenCode 設定目錄：

- `commands/` → `~/.config/opencode/commands/`
- `skills/ddd-arch/` → `~/.agents/skills/clean-ddd-hexagonal/`
- `skills/ddd-refactor/` → `~/.agents/skills/moai-workflow-ddd/`
