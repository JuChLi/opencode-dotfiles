---
description: 系統化除錯流程（先找根因再修復）
---
Find root cause before attempting fixes. No guessing.

## Instructions

Load the `systematic-debugging` skill and follow the four-phase process.

$ARGUMENTS

## Steps

1. Use the Skill tool to load the `systematic-debugging` skill
2. Follow the four phases:
   - **Phase 1 - Root Cause**: Read errors, reproduce, check changes, trace data flow
   - **Phase 2 - Pattern Analysis**: Find working examples, compare differences
   - **Phase 3 - Hypothesis**: Form single hypothesis, test minimally
   - **Phase 4 - Implementation**: Create failing test, fix, verify
3. Do NOT propose fixes without completing Phase 1
4. If 3+ fixes fail, question the architecture
