---
name: doc-creator
description: 使用台灣繁體中文產生、重構與品質檢查技術文件（Markdown），可切換 Google developer documentation style 與業界常用規範（Diataxis/Write the Docs），並透過 Python quality gate 保障章節結構一致、術語一致、文風可讀與重複內容偵測。當需要撰寫規格、計畫、操作手冊、參考文件、說明文件或交接文件時使用。
---

# Doc Creator

為技術文件提供「可撰寫、可重構、可驗證」的標準流程，並預設以台灣繁體中文輸出。

## 核心流程

1. 判定文件類型：`tutorial`、`how-to`、`reference`、`explanation` 或 `handoff`。
2. 選擇風格設定檔：`google-zhtw`、`industry-zhtw`、`handoff-zhtw` 或 custom profile。
3. 套用對應模板產出初稿（`references/templates/`）。
4. 執行 quality gate：
   - `validate_structure.py`：章節完整度（hard fail）
   - `check_terminology.py`：術語一致性（hard fail）
   - `lint_prose_zhtw.py`：文風可讀性（warning）
   - `detect_similarity.py`：重複/高度相似內容（warning）
5. 依檢查結果修正文稿，直到 hard fail 全部清除。
6. 需要嚴格模式時使用 `quality_gate.py --strict`，把 warning 升級為 fail。

## 規範層級

1. 專案既有規範（若存在）
2. `google-zhtw`（Google developer documentation style 對齊）
3. `industry-zhtw`（Diataxis + Write the Docs 的通用基線）
4. `handoff-zhtw`（交接場景加強版）

若發生衝突，優先遵循專案規範，並在同一份文件中保持一致。

## 指令範例

```bash
# 1) 以 Google 風格執行完整 quality gate
python scripts/quality_gate.py --root docs --style google-zhtw

# 2) 嚴格模式：warning 也會阻擋
python scripts/quality_gate.py --root docs --style google-zhtw --strict

# 3) 僅檢查章節結構
python scripts/validate_structure.py --root docs --style industry-zhtw

# 4) 僅檢查術語一致性
python scripts/check_terminology.py --root docs --style google-zhtw

# 5) 找重複或高度相似文件
python scripts/detect_similarity.py --root docs --style industry-zhtw --threshold 0.9

# 6) 從外部規範建立 custom profile 草稿
python scripts/extract_style_profile.py \
  --name my-team-style \
  --source "https://developers.google.com/style" \
  --extends google-zhtw \
  --output references/style-profiles/my-team-style.json
```

## 預設品質政策

- `hard fail`：結構缺漏、術語違規。
- `warning`：文風可讀性、內容相似度。
- `--strict`：所有 warning 升級為 fail（適合發版前或文件凍結期）。

## 參考文件

- `references/doc-taxonomy-diataxis.md`
- `references/high-quality-checklist.md`
- `references/terminology-glossary.md`
- `references/style-source-discovery.md`
- `references/templates/tutorial.md`
- `references/templates/how-to.md`
- `references/templates/reference.md`
- `references/templates/explanation.md`
- `references/templates/handoff.md`
- `references/style-profiles/industry-zhtw.json`
- `references/style-profiles/google-zhtw.json`
- `references/style-profiles/handoff-zhtw.json`
- `references/style-profiles/custom-template.json`
