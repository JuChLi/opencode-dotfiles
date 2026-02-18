---
name: ddd-refactor-v2
description: 使用 ANALYZE-PRESERVE-IMPROVE 進行既有程式碼的行為保留式重構（DDD refactoring），內建明確決策閘門、可交付輸出契約、風險分級與失敗回復流程。適用於 legacy refactor、技術債重整、API 遷移（行為不變）。不適用於從零開發新功能或明確改變業務行為。
---

# DDD Refactor v2

以「行為不變」為核心的重構工作流，提供明確進入條件、逐步驗證與可交接產物。

## 快速決策閘門

先做分類，避免把不同工作類型混在同一流程：

1. `existing code + behavior must stay` -> 用本技能（DDD refactor）。
2. `new feature / new module from scratch` -> 改用 TDD 流程。
3. `business behavior must change` -> 先更新規格，再決定走功能實作或重構。

若需求同時包含「重構」與「改行為」，請先分兩張任務卡處理，避免驗證基線污染。

## 核心原則

- 觀察到的行為（外部 API、副作用、錯誤語意）在重構前後必須一致。
- 每次只做小步驟變更，且每一步都要可回退。
- 先建立安全網，再做結構改善。
- 驗證證據優先於口頭宣告。

## 標準流程：ANALYZE -> PRESERVE -> IMPROVE

### Phase 1: ANALYZE

目標：搞清楚改動邊界與風險，不急著改碼。

- 盤點邊界：哪些檔案、模組、入口點會受影響。
- 標記風險：高風險路徑（交易、金流、授權、序列化、時序）。
- 識別壞味道：高耦合、重複邏輯、過長方法、錯誤責任分配。
- 定義本輪目標：本輪只解 1-2 類結構問題。

輸出要求與完成條件請看 `references/workflow-gates.md`。

### Phase 2: PRESERVE

目標：建立行為安全網與比對基線。

- 先跑現有測試，記錄基線結果。
- 對將修改的路徑補 characterization tests。
- 必要時加入 snapshot（序列化、錯誤訊息、事件輸出）。
- 確保測試穩定（不可 flaky）再進入下一階段。

### Phase 3: IMPROVE

目標：在不改行為前提下，逐步改善結構。

- 單一步驟改動：一次只做一個結構性調整。
- 變更後立即驗證：先快測，再整套測試。
- 失敗立即回退：不要把多個可疑變更混在同一批。
- 每輪收斂：記錄「做了什麼、為何、證據是什麼」。

## 強制輸出契約

每輪重構都必須產出以下文件（可放在 `.refactor/<ticket>/`）：

1. `analysis.md`
2. `preserve.md`
3. `improve-log.md`
4. `validation.md`
5. `summary.md`

格式與欄位見 `references/output-contract.md`。

可用腳本快速生成骨架：

```bash
python skills/ddd-refactor-v2/scripts/init_refactor_artifacts.py --ticket TICKET-123
```

## 常見失敗模式

- 邊改邊補測，導致基線與新行為混在一起。
- 一次改太多，無法定位回歸來源。
- 只看測試綠燈，沒有檢查外部可觀測行為（API/事件/錯誤碼）。
- 把本該改規格的工作硬塞進「行為保留式重構」。

## 與舊版 ddd-refactor 的差異

- 移除 greenfield/superset 的混淆敘述，聚焦既有程式碼重構。
- 增加明確 workflow gates（入口、出口、阻擋條件）。
- 增加 output contract，確保可交接與可審核。
- 增加 recovery playbook，避免失敗時卡住。

## 參考文件

- `references/workflow-gates.md`
- `references/output-contract.md`
- `references/refactor-checklist.md`
- `references/recovery-playbook.md`
