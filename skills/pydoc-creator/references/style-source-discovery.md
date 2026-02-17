# Python 文件風格來源盤點指引

當使用者指定特定框架或套件風格時，先確認可追溯的官方來源，避免引用品質不明的二手資料。

## 1) 優先來源

1. Python 官方文件與 PEP（例如 PEP 257）。
2. 官方專案文件站（ReadTheDocs、官方 docs site）。
3. 官方 GitHub repository（`CONTRIBUTING.md`、style guide、doc templates）。

避免將來源不明的部落格當成唯一依據。

## 2) 搜尋關鍵字

建議用「套件名 + 下列關鍵字」搜尋：

- `docstring style`
- `documentation style`
- `contributing`
- `coding style`
- `api reference`

## 3) 取得後的轉換流程

1. 使用 `scripts/extract_style_profile.py` 產生 profile JSON 初稿。
2. 人工挑選可機械執行的規則（summary / params / returns / raises）。
3. 將規則寫入 `references/style-profiles/<name>.json`。
4. 用 `--style-file` 套用並執行 lint 驗證。

## 4) Python 官方與 Google 風格備註

- PEP 257 強調摘要句與段落結構，但不綁定單一標記格式。
- Google Python Style Guide 提供可機械化的區段格式（`Args` / `Returns` / `Raises`）。
- 若採 Google 風格，建議同時要求 `Examples` 區段以提升可讀性與可驗證性。
- 實務上仍需以目標專案官方文件為準。

## 5) 驗證清單

- 規則是否來自官方文件或官方 repo。
- 規則是否能轉成 profile 欄位。
- 套用後是否通過 `lint_docstrings.py`。
