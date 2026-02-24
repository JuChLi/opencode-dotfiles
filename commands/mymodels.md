---
description: 依任務推薦最適模型
---
Use `mymodels` policy to recommend a model for the user task.

## User Query

$ARGUMENTS

## Data Sources

- Machine config: `D:\opencode\opencode-dotfiles\opencode-mymodels\references\models.json`
- Human guide: `D:\opencode\opencode-dotfiles\opencode-mymodels\readme.md`

## Workflow

1. Read `models.json` and follow `policy`.
2. Classify request into one of:
   - `quick_fix`
   - `general_coding`
   - `deep_debug`
   - `repo_wide_refactor`
   - `plan_mode` / `build_mode` when user explicitly asks.
3. Recommend from `recommended` and route defaults first.
4. Do not pick models in `avoid_by_default` unless user explicitly asks or task escalation is required.
5. Return concise output in Traditional Chinese with:
   - 主推薦模型
   - 備用模型
   - 升級模型（必要時）
   - 簡短理由（成本/效果）

If `$ARGUMENTS` is empty, ask the user for task type and expected priority (省 token / 品質優先).
