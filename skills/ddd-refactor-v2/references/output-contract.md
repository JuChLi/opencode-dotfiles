# Output Contract

每輪 DDD refactor 產物必須完整，避免只留下「我改好了」但無法交接。

建議目錄：`.refactor/<ticket>/`

## 1) analysis.md

必要欄位：

- Scope
- Code boundaries
- Risk map (high/medium/low)
- Refactor targets
- Out of scope

## 2) preserve.md

必要欄位：

- Existing test baseline
- Added characterization tests
- Snapshot/baseline artifacts
- Safety-net gaps

## 3) improve-log.md

必要欄位：

- Step-by-step changes
- Why each step was done
- Validation command per step
- Rollback note (if any)

## 4) validation.md

必要欄位：

- Behavior checks (API/output/error/event)
- Test results (unit/integration/characterization)
- Performance guardrail (if applicable)
- Regression findings

## 5) summary.md

必要欄位：

- What improved structurally
- What behavior stayed identical
- Known limitations
- Next safe refactor slice
