---
name: javadoc-creator
description: 使用台灣繁體中文產生、精修與 lint 高品質 Java Javadoc，並可切換 Vert.x、Apache、Google Java Style 或自訂 style profile。所有輸出需先符合 Javadoc 官方 Documentation Comment Specification for the Standard Doclet，再套用專案風格。當使用者需要大量補齊 Javadoc、提升註解品質、對齊特定框架/函式庫風格，或把模板註解升級為可維護的 API 文件時使用。
---

# Javadoc Creator

為 Java（特別是 reactive codebase）產生高品質 Javadoc，並提供可明確控制的風格機制。

## 核心流程

1. 決定風格來源：
   - 使用內建 profile（`vertx`、`apache`、`google`），或
   - 由使用者提供的 style guide URL/檔案建立 custom profile。
2. 先用 `scan_missing_javadocs.py` 掃描目前覆蓋率。
3. 用 `generate_javadocs.py` 補齊缺漏。
4. 用 `refine_javadocs.py` 精修文字品質。
5. 用 `lint_javadocs.py` 作為風格與品質閘門。
6. 收尾前執行 compile/test 驗證。

## 風格選擇

### 內建風格

- `vertx`: 摘要精簡，強調非同步語意。
- `apache`: 保守、明確、偏 Apache 風格語氣。
- `google`: 對齊 Google Java Style Guide `§7 Javadoc`（summary fragment、tag 順序、`@deprecated` 規範）。
- `beginner-zhtw`: 以初學者可讀性為優先，使用白話、明確且避免術語堆疊。

### 從外部來源建立自訂風格

若使用者指定其他風格（例如特定 Apache 子專案，或任一函式庫風格）：

1. 找到官方風格來源 URL/文件。
2. 執行 `extract_style_profile.py` 產生 profile JSON。
3. 人工調整生成結果（`methodSummary` / `paramDescriptions` / `bannedPatterns`）。
4. 在 generate/refine/lint 階段加上 `--style-file` 套用。

## 指令範例

```bash
# 1) 掃描（以 Vert.x 風格為基準）
python scripts/scan_missing_javadocs.py --root src/main/java --style vertx

# 2) 以 Google 風格補齊缺漏
python scripts/generate_javadocs.py --root src/main/java --style google

# 3) 以同一風格精修文字
python scripts/refine_javadocs.py --root src/main/java --style google

# 4) 執行品質閘門
python scripts/lint_javadocs.py --root src/main/java --style google

# 5) 初學者可讀模式
python scripts/generate_javadocs.py --root src/main/java --style beginner-zhtw
```

```bash
# 從 URL 建立 custom profile（Python 3.10+）
python scripts/extract_style_profile.py \
  --name commons-lang-style \
  --source "https://example.org/javadoc-style-guide" \
  --extends apache \
  --output references/style-profiles/commons-lang-style.json

# 套用 custom profile
python scripts/generate_javadocs.py --root src/main/java --style vertx \
  --style-file references/style-profiles/commons-lang-style.json
```

## 約束

- 先符合 `Documentation Comment Specification for the Standard Doclet` 核心規範，再套用風格差異。
- 若使用 `google` 風格，摘要需符合 summary fragment 慣例（避免 `This method ...`/「此方法...」句型）。
- 產生內容使用台灣繁體中文（`zh-TW`）。
- 不使用 emoji 或裝飾符號。
- 摘要首句需聚焦行為與用途。
- block tags 需遵守核心順序：`@param` -> `@return` -> `@throws`。
- 若出現 `@deprecated`，需提供棄用原因與替代 API（建議使用 `{@link ...}`）。
- 非 `void` 且非建構子方法需有 `@return`；`void`/建構子不可出現 `@return`。
- 對 `Future` 回傳型別需描述非同步完成語意。
- 避免低資訊句型（例如「操作結果」「方法輸入參數」）。

## 參考文件

- `references/terminology-glossary.md`
- `references/documentation-comment-spec.md`
- `references/vertx-javadoc-style.md`
- `references/high-quality-checklist.md`
- `references/style-source-discovery.md`
- `references/style-profiles/vertx.json`
- `references/style-profiles/apache.json`
- `references/style-profiles/google.json`
- `references/style-profiles/beginner-zhtw.json`
- `references/style-profiles/custom-template.json`
