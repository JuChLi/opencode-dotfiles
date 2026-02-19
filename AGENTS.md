# OpenCode Dotfiles

## 重要原則

- **全域或專案設定請找 `.agents/` 或 `.config/`**：除非使用者特別說明，否則不應該去 `~/.claude/` 目錄找東西。如果有疑問，請先提出並等待確認。

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
- `skills/skill-creator/` → `~/.agents/skills/skill-creator/`
