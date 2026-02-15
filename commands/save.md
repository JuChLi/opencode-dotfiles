---
description: 儲存目前專案進度到 SESSION.md
---
請自動更新目前專案的 SESSION.md 檔案，依序執行以下步驟：

## 1. 收集資訊
- 執行 `git log --oneline -10` 查看最近提交
- 檢查 docs/plans/ 目錄的計畫文件
- 檢查 AGENTS.md 了解專案結構

## 2. 更新 SESSION.md
在專案根目錄建立或更新 SESSION.md，使用以下格式：

```markdown
# Session Summary

> 自動產生於 [當前日期時間]
> 專案：[專案名稱]

## 目前進度

### 已完成
- [從 git log 提取最近 5-10 個有意義的 commit，用簡短描述]

### 進行中
- [從對話上下文或 plans/ 目錄判斷]

### 待完成
- [從 plans/ 目錄的 pending 項目或 roadmap 提取]

## 下一步
- [根據待完成項目，建議 1-3 個具體下一步]

## 最近 Commits
[貼上 git log --oneline -5 的結果]

## 相關文件
- [列出 docs/plans/ 中的相關檔案]
```

## 3. 確認
- 顯示更新後的 SESSION.md 內容摘要
- 詢問使用者是否要 commit 這個變更
