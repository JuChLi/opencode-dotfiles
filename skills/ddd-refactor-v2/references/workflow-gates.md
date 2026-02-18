# Workflow Gates

本文件定義每個 phase 的進入條件（Entry）、出口條件（Exit）與阻擋條件（Blockers）。

## 1) ANALYZE Gate

### Entry

- 已確認這是「既有程式碼」重構，不是新功能開發。
- 已有目標範圍（模組、檔案或功能邊界）。

### Exit

- 有明確重構目標（例如降低耦合、拆分責任、移除重複）。
- 有風險分級（高/中/低）與優先序。
- 已列出本輪「不做」清單（out of scope）。

### Blockers

- 無法明確界定邊界。
- 需求本質是「改行為」但規格未更新。

## 2) PRESERVE Gate

### Entry

- ANALYZE 已完成且有可追蹤輸出。

### Exit

- 現有測試可穩定執行。
- 受影響路徑已有 characterization tests。
- 重要可觀測輸出已建立 baseline（必要時 snapshot）。

### Blockers

- 測試基線不穩定（flaky）。
- 缺少關鍵路徑測試，且短期無法補足。

## 3) IMPROVE Gate

### Entry

- PRESERVE 基線完整，且有明確回退策略。

### Exit

- 重構目標達成（至少一項可量化改善）。
- 所有 baseline 驗證通過。
- 變更說明與證據已記錄於 validation/summary。

### Blockers

- 任一步驟出現不可解回歸。
- 雖通過測試，但外部行為明顯改變。
