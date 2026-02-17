---
name: pydoc-creator
description: 使用台灣繁體中文產生、精修與 lint 高品質 Python docstring（module/class/function/method），並可切換 PEP 257（Python 官方）或 Google Style 風格。當使用者需要大量補齊 docstring、提升註解品質、對齊 Python 官方文件或 Google Style 範本，或將模板註解升級為可維護 API 文件時使用。
---

# Python Docstring Creator

為 Python 專案產生高品質 docstring，並提供可機械化執行的風格控制機制。

## 核心流程

1. 決定風格來源：
   - 使用內建 profile（`pep257`、`google`），或
   - 由使用者提供官方風格來源 URL/文件，建立 custom profile。
2. 先用 `scan_missing_docstrings.py` 掃描目前覆蓋率。
3. 用 `generate_docstrings.py` 補齊缺漏。
4. 用 `refine_docstrings.py` 精修弱摘要與模板句。
5. 用 `lint_docstrings.py` 作為風格與品質閘門。
6. 收尾前執行 `pytest` 或專案既有測試驗證。

## 風格選擇

### 內建風格

- `pep257`: 參考 Python 官方 PEP 257，採摘要 + 詳細描述，並以 reST 標記（`:param` / `:returns` / `:raises`）呈現欄位。
- `google`: 參考 Google Python Style Guide，採摘要 + 詳細描述 + `Args` / `Returns` / `Raises` / `Examples` 區段。

### 從外部來源建立自訂風格

若使用者指定其他風格（例如 Requests、Pandas、FastAPI 或公司內部規範）：

1. 找到官方文件站或官方 repo 的 style guide URL。
2. 執行 `extract_style_profile.py` 產生 profile JSON 初稿。
3. 人工調整生成結果（`functionSummary` / `paramDescriptions` / `bannedPatterns`）。
4. 在 generate/refine/lint 階段加上 `--style-file` 套用。

## 指令範例

```bash
# 1) 掃描（以 PEP 257 為基準）
python scripts/scan_missing_docstrings.py --root src --style pep257

# 2) 以 Google Style 補齊缺漏
python scripts/generate_docstrings.py --root src --style google

# 3) 以同一風格精修文字品質
python scripts/refine_docstrings.py --root src --style google

# 4) 執行品質閘門
python scripts/lint_docstrings.py --root src --style google
```

```bash
# 從 URL 建立 custom profile（Python 3.10+）
python scripts/extract_style_profile.py \
  --name requests-style \
  --source "https://requests.readthedocs.io/en/latest/" \
  --extends pep257 \
  --output references/style-profiles/requests-style.json

# 套用 custom profile
python scripts/generate_docstrings.py --root src --style pep257 \
  --style-file references/style-profiles/requests-style.json
```

## 約束

- 產生內容使用台灣繁體中文（`zh-TW`）。
- 不使用 emoji 或裝飾符號。
- 摘要首句需聚焦行為與用途，不可只重複函式名稱。
- 摘要後需有至少一段詳細描述（用途、限制、注意事項）。
- `async def` 需描述非同步完成語意。
- Google 風格需包含 `Examples` 區段；PEP 257 風格需維持官方段落結構與一致欄位標記。
- 避免低資訊句型（例如「執行某功能」「輸入參數」）。

## 參考文件

- `references/terminology-glossary.md`
- `references/python-docstring-style.md`
- `references/high-quality-checklist.md`
- `references/style-source-discovery.md`
- `references/style-profiles/pep257.json`
- `references/style-profiles/google.json`
- `references/style-profiles/custom-template.json`
