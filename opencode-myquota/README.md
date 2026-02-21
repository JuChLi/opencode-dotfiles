# opencode-myquota

查詢所有 AI 帳號配額（GitHub Copilot、OpenAI、Z.ai、MiniMax）

## 安裝流程

### 前置需求
- Bun 已安裝（用於 OpenCode 插件依賴）
- OpenCode 已安裝

### 步驟

```powershell
# 1. 複製專案
git clone https://github.com/JuChLi/opencode-dotfiles.git
cd opencode-dotfiles/opencode-myquota

# 2. 執行安裝腳本
.\install.ps1

# 3. 重啟 OpenCode
```

### 驗證

```
/myquota
```

## 運作原理

- 編譯後的插件放在 `plugins/myquota/`
- OpenCode 會自動載入 `~/.config/opencode/plugins/` 目錄下的本地插件
- Command 會自動從 `commands/` 目錄載入
- **不需要**將 `opencode-myquota` 加入 `opencode.json` 的 `plugin` 陣列

## 常見問題

### Q: 出現 BunInstallFailedError？
A: 確保 Bun 已安裝並在 PATH 中

### Q: 插件沒反應？
A: 確認 `opencode.json` 中**沒有** `opencode-myquota` 在 plugin 陣列內

## 認證設定

確保 auth.json 中有對應的 provider：

| Provider | Node Name |
|----------|-----------|
| GitHub Copilot | `github-copilot` |
| OpenAI | `openai` |
| Z.ai | `zai-coding-plan` |
| MiniMax | `minimax-coding-plan` |
