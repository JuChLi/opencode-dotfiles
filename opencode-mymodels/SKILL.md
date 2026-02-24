---
name: mymodels
description: 依任務推薦最合適模型
---

# OpenCode MyModels - Model 選擇器

## 概述

本 Skill 幫助使用者根據任務類型、複雜度和預算，選擇最適合的 AI Model，以達到 Token 消耗最小化與效果最大化的目標。

## 觸發方式

| 指令 | 說明 |
|------|------|
| `/mymodels` | 進入 model 選擇模式 |
| `/mymodels plan` | 查詢 Plan 階段預設模型 |
| `/mymodels build` | 查詢 Build 階段預設模型 |
| `/mymodels guide` | 顯示完整指南位置 |
| `/mymodels quick` | 顯示快速參考表 |

## 使用者 Provider 等級

| Provider | 等級 | 可用模型 |
|----------|------|----------|
| MiniMax | Plus | M2.1, M2.5, M3 |
| GLM | Pro | GLM-4, GLM-4-flash |
| GPT | Plus | GPT-4o, GPT-4o-mini, o1-mini |
| GitHub Copilot | Pro+ | Copilot (最高級) |

## 決策流程

### Step 1: 判斷任務類型

```
任務類型
├─ Code Completion（代碼補全）──→ Copilot Pro+（首選）
├─ Code Review（代碼審查）─────→ Step 2
├─ Code Writing（代碼撰寫）────→ Step 2
├─ Debugging（除錯）────────────→ Step 2
├─ Refactoring（重構）─────────→ Step 2
└─ Documentation（文檔）───────→ Step 2
```

### Step 2: 判斷任務複雜度

| 複雜度 | 判斷標準 | 推薦模型 |
|--------|----------|----------|
| **簡單** | 單一檔案、单一功能、語法錯誤 | MiniMax-M2.1 / GLM-4-flash |
| **中等** | 2-5 個檔案、需要理解邏輯 | MiniMax-M2.5 / GLM-4 |
| **複雜** | 多檔案、架構設計、深度推理 | MiniMax-M3 / GPT-4o |
| **極複雜** | 系統級、困難演算法、深度除錯 | o1-mini |

### Step 3: 考慮特殊因素

| 因素 | 建議 |
|------|------|
| 需要中文理解 | 優先 MiniMax |
| 需要最新技術知識 | 優先 GPT-4o |
| 預算優先 | 優先 MiniMax-M2.1 / GLM-4-flash |
| 品質優先 | 優先 GPT-4o / o1-mini |

## 預設模型配置（Plan/Build）

| 階段 | 預設模型 | 理由 |
|------|---------|------|
| **Plan** | MiniMax-M2.5 | 推理能力足夠、成本適中、速度快 |
| **Build** | MiniMax-M2.5 | 實作需要較好理解力 |

複雜任務可升級為 GPT-4o。

## 常見情境推薦

### 日常 Coding（佔 60%）
- **首選**：GitHub Copilot Pro+
- **理由**：零對話 token 成本，即時補全

### 中等複雜度任務（佔 25%）
- **首選**：MiniMax-M2.5
- **備用**：GLM-4
- **理由**：成本適中，效果好

### 高難度任務（佔 10%）
- **首選**：GPT-4o
- **理由**：推理能力強

### 極困難問題（佔 5%）
- **首選**：o1-mini
- **理由**：專用於深度推理

## Token 優化原則

1. **小問題用小模型**：不要用 GPT-4o 處理 M2.1 就能做的任務
2. **控制 context**：只提供相關檔案，避免無效 token
3. **善用 Copilot**：日常補全優先使用，節省對話 token
4. **streaming**：即時看到輸出，提前終止不需要的回應

## 參考文檔

| 文件 | 說明 |
|------|------|
| [MODEL_QUICK_REF.md](references/MODEL_QUICK_REF.md) | 精簡版模型對照表（1-2 頁） |
| [MODEL_FULL_GUIDE.md](references/MODEL_FULL_GUIDE.md) | 完整版使用指南（5-10 頁） |

## 回應格式

當使用者觸發 `/mymodels` 時，請根據以下格式回應：

```
## Model 推薦

| 項目 | 內容 |
|------|------|
| **任務類型** | [任務描述] |
| **推薦模型** | [模型名稱] |
| **理由** | [簡短說明] |
| **預估 token** | [低/中/高] |
| **備用模型** | [備用選項] |

如需調整，請告訴我你的需求：
- 要更便宜？
- 要更高品質？
- 有特定偏好？
```
