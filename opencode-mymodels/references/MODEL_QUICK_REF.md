# Model 快速參考表

## 模型對照總表

| 等級 | MiniMax (Plus) | GLM (Pro) | GPT (Plus) | Copilot (Pro+) |
|------|----------------|-----------|------------|----------------|
| **基礎** | M2.1 | GLM-4-flash | GPT-4o-mini | Copilot |
| **中等** | M2.5 | GLM-4 | GPT-4o | - |
| **進階** | M3 | - | o1-mini | - |
| **頂級** | - | - | o1-preview | - |

---

## 任務 → 模型速查

### Code Completion

| 任務 | 首選模型 |
|------|----------|
| 函式內補全 | Copilot Pro+ |
| 整行/整塊補全 | Copilot Pro+ |

### Code Review

| 複雜度 | 首選模型 |
|--------|----------|
| 簡單 | MiniMax-M2.1 |
| 中等 | MiniMax-M2.5 |
| 複雜 | GPT-4o |

### Code Writing

| 複雜度 | 首選模型 |
|--------|----------|
| 簡單 | MiniMax-M2.1 |
| 中等 | MiniMax-M2.5 |
| 複雜 | MiniMax-M3 / GPT-4o |
| 極複雜 | o1-mini |

### Debugging

| 類型 | 首選模型 |
|------|----------|
| 語法錯誤 | MiniMax-M2.1 |
| Runtime error | MiniMax-M2.5 |
| 邏輯 bug | GPT-4o |
| 困難問題 | o1-mini |

### Refactoring

| 類型 | 首選模型 |
|------|----------|
| 命名優化 | MiniMax-M2.1 |
| 函式拆分 | MiniMax-M2.5 |
| 設計模式 | MiniMax-M2.5 / GPT-4o |
| 大規模重構 | GPT-4o |

---

## 使用比例建議

```
40% → Copilot Pro+
20% → MiniMax-M2.1
15% → MiniMax-M2.5
10% → GLM-4
10% → GPT-4o
 5% → o1-mini
```

---

## 快速決策

```
是簡單重複性工作？ → Copilot Pro+
        │
        否
        ▼
需要深度推理？ → 是 → o1-mini / GPT-4o
        │
        否
        ▼
涉及中文？ → 是 → MiniMax-M2.5
        │
        否
        ▼
任務複雜度？
  ├─ 簡單 → MiniMax-M2.1
  ├─ 中等 → MiniMax-M2.5
  └─ 複雜 → GPT-4o
```
