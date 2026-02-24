# mymodels 使用說明

這份是給人看的手冊；機器請讀 `references/models.json`。

## 核心規則

- `available` 放「你目前可用的全部模型」。
- `avoid_by_default` 放「版本號最大的模型」，可用但預設先不選。
- `recommended` 不放版本號最大的模型。
- `defaults` 和 `routing` 的預設優先，不放版本號最大的模型。
- 真的需要最高版本時，才手動升級使用。

## 常用指令

- `/mymodels`：一般模型推薦
- `/mymodels plan`：看 Plan 階段預設
- `/mymodels build`：看 Build 階段預設
- `/mymodels quick`：快速建議
- `/mymodels guide`：完整說明

## 你可以這樣問

- `/mymodels 幫我挑一個省 token 的 model`
- `/mymodels 這個 bug 很難，先幫我排優先順序`
- `/mymodels 這次要做 repo 大重構，先選模型`

## Provider 規劃

### OpenAI (ChatGPT Plus)

- Recommended: `gpt-5.1 Codex mini`, `gpt-5.1 Codex`, `gpt-5.2`
- Highest version: `gpt-5.3 Codex`
- Avoid by default: `gpt-5.3 Codex`, `gpt-5.2 Codex`, `gpt-5.1 Codex Max`
- 說明：先走 mini 或一般 Codex，最高版本留作手動升級。

### GitHub Copilot (Pro+)

- Recommended: `Claude Sonnet 4.5`, `Claude Haiku 4.5`
- Highest versions: `Claude Sonnet 4.6`, `Claude Opus 4.6`
- Avoid by default: `Claude Sonnet 4.6`, `Claude Opus 4.6`, `Claude Opus 4.5`
- 說明：日常優先 Sonnet/Haiku，Opus 和 4.6 版本先不預設選。

### Z.ai GLM (Pro)

- Recommended: `glm-4.6`, `glm-4.5-Air`, `glm-4.5`
- Highest versions: `glm-4.7`, `glm-4.7-Flash`, `glm-4.7-FlashX`
- Avoid by default: `glm-4.7`, `glm-4.7-Flash`, `glm-4.7-FlashX`, `glm-4.6V`, `glm-4.5V`
- 說明：平常先用 4.6/4.5 系列，4.7 系列保留給手動升級。

### MiniMax (Plus)

- Recommended: `minimax-m2.1`, `minimax-m2`
- Highest version: `minimax-m2.5`
- Avoid by default: `minimax-m2.5`
- 說明：以 `m2.1` 做常駐省 token，`m2.5` 不當預設。

## 預設模型

### Plan mode

- Primary: `minimax-m2.1`
- Fallback: `glm-4.6`
- Escalation: `gpt-5.1 Codex`

### Build mode

- Primary: `minimax-m2.1`
- Fallback: `gpt-5.1 Codex mini`
- Escalation: `gpt-5.1 Codex`

## 任務路由

- `quick_fix`: `Claude Haiku 4.5` -> `minimax-m2.1` -> `glm-4.5-Air`
- `general_coding`: `minimax-m2.1` -> `Claude Sonnet 4.5` -> `gpt-5.1 Codex mini`
- `deep_debug`: `gpt-5.1 Codex` -> `Claude Sonnet 4.5` -> `glm-4.6`
- `repo_wide_refactor`: `gpt-5.1 Codex` -> `Claude Sonnet 4.5` -> `minimax-m2.1`

## 維護流程

1. Provider 更新時，先更新 `references/models.json` 的 `available`
2. 把最大版本同步更新到 `highest_versions` + `avoid_by_default`
3. 確認 `recommended`、`defaults`、`routing` 沒有用到最大版本
4. 最後更新這份 `readme.md`
