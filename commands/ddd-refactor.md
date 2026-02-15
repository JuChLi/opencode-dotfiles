---
description: DDD workflow for behavior-preserving refactoring
---
Domain-Driven Development workflow for behavior-preserving code transformation.

## Usage

Use this command when:
- Refactoring legacy code
- Improving code structure without functional changes
- Reducing technical debt
- Performing API migration with behavior preservation

Do NOT use for:
- Writing new tests (use TDD instead)
- Creating new features from scratch

## Instructions

Load the `ddd-refactor` skill and execute the ANALYZE-PRESERVE-IMPROVE cycle.

$ARGUMENTS

## Steps

1. Use the Skill tool to load the `ddd-refactor` skill
2. Follow the three-phase workflow:
   - **ANALYZE**: Domain boundary identification, coupling metrics, AST structural analysis
   - **PRESERVE**: Characterization tests, behavior snapshots, test safety net verification
   - **IMPROVE**: Incremental structural changes with continuous behavior validation
3. Apply safe refactoring patterns as documented in the skill
4. Validate behavior preservation after each transformation
