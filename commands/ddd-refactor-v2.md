---
description: DDD 重構 v2（明確 Gate + 輸出契約 + 回復流程）
---
Run behavior-preserving refactoring with ANALYZE-PRESERVE-IMPROVE and explicit workflow gates.

## Usage

Use this command when:
- Refactoring existing code while preserving behavior
- Reducing technical debt in legacy modules
- Reorganizing code structure without changing business outcomes
- Performing API migration with compatibility guarantees

Do NOT use for:
- Building new features from scratch (use TDD workflow)
- Intentional business behavior changes before spec updates

## Instructions

Load the `ddd-refactor-v2` skill and execute the gated workflow with mandatory artifacts.

$ARGUMENTS

## Steps

1. Use the Skill tool to load `ddd-refactor-v2`
2. Run the entry decision gate (refactor vs new feature vs behavior change)
3. Execute ANALYZE -> PRESERVE -> IMPROVE in small, reversible steps
4. Produce required artifacts (`analysis`, `preserve`, `improve-log`, `validation`, `summary`)
5. Verify behavior equivalence before claiming completion
