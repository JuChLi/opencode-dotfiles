---
description: 查詢目前專案的進度狀態
---
請檢查目前專案的進度狀態，依序執行以下步驟：

## 1. 基本資訊
- 讀取 AGENTS.md（如果存在）了解專案概述
- 執行 `git log --oneline -5` 查看最近提交

## 2. 進度追蹤
檢查以下檔案（如果存在）：
- SESSION.md 或 .opencode/SESSION.md - Session 進度
- docs/plans/ 目錄 - 實作計畫和待辦事項
- TODO.md - 待辦清單

## 3. 輸出摘要
請用以下格式回報：

```
📁 專案：[專案名稱]
📍 位置：[目前目錄]

✅ 最近完成：
- [從 git log 摘要]

🔄 進行中/待完成：
- [從 plans 或 SESSION.md 摘要]

📋 下一步建議：
- [根據上述資訊建議]
```

如果找不到任何進度資訊，建議使用者建立 SESSION.md 來追蹤進度。
