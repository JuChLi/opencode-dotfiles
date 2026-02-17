# 風格來源盤點指引

當使用者指定特定框架或函式庫風格時，先確認可追溯的官方來源，避免引用品質不明的二手資料。

在任何風格來源之前，先以 `Documentation Comment Specification for the Standard Doclet` 作為共同基線。

## 1) 優先來源

1. 官方專案文件站（docs site）
2. 官方 GitHub repository（`CONTRIBUTING.md`、`STYLEGUIDE`、`checkstyle`）
3. 官方 API/Javadoc 文件（用於術語與句型偏好）

避免將來源不明的部落格當成唯一依據。

## 2) 搜尋關鍵字

建議用「專案名 + 下列關鍵字」搜尋：

- `javadoc style`
- `documentation style`
- `contributing`
- `checkstyle`
- `code style`

## 3) 取得後的轉換流程

1. 使用 `scripts/extract_style_profile.py` 產生 profile JSON 初稿。
2. 人工挑選真正可落地執行的規則（summary / `@param` / `@return` / `@throws`）。
3. 將規則寫入 `references/style-profiles/<name>.json`。
4. 檢查規則是否仍符合 Standard Doclet 核心語法與 tag 結構。
5. 用 `--style-file` 套用並執行 lint 驗證。

## 4) Apache 類風格備註

- Apache 生態常以簡潔、保守、明確為主。
- 仍需以該專案官方文件為準，不可假設所有 Apache 子專案一致。

## 5) 驗證清單

- 規則是否來自官方文件或官方 repo。
- 是否符合 `Documentation Comment Specification for the Standard Doclet`。
- 規則是否能轉成可機械執行的 profile 欄位。
- 套用後是否通過 `lint_javadocs.py`。
