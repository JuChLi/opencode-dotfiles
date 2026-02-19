---
description: 建立/更新 Skill 的工作流程指南
---

Create or update an agent skill package (SKILL.md + optional resources).

## Prereq

Ensure the `skill-creator` skill is installed (available to the Skill tool).

## Instructions

Load the `skill-creator` skill and follow its workflow.

$ARGUMENTS

## Steps

1. Use the Skill tool to load the `skill-creator` skill（先把 skill 載進來，後面才有完整流程可以照著做）
2. Elicit concrete usage examples and triggers（先收集幾個實際會怎麼用的例子，避免做出用不到/不好觸發的技能）
3. Design the skill structure (SKILL.md + scripts/references/assets as needed)（先把檔案怎麼拆、怎麼放想清楚，之後才不會越做越亂）
4. Keep SKILL.md concise; move long content into references/（SKILL.md 盡量短一點，長內容丟 references/，比較省 context）
5. Package/validate the skill when ready（最後再打包/驗證一下，確認格式對、裝得起來、用得動）
