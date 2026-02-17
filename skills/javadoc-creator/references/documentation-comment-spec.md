# Documentation Comment Specification（Standard Doclet）重點

本文件整理 Javadoc 官方規範的核心要求，作為 `javadoc-creator` 的最低基線。

官方規格文件（JDK）：

- `Documentation Comment Specification for the Standard Doclet`
- 建議參考：`https://docs.oracle.com/en/java/javase/17/docs/specs/javadoc/doc-comment-spec.html`

## 1) 基本結構

- 使用 `/** ... */` 作為文件註解。
- 第一段為摘要句（summary sentence）。
- 摘要後可有詳細描述。
- block tags（例如 `@param`）需放在主描述之後。

## 2) block tags 核心規範

- `@param <name>`：每個方法參數應有對應說明。
- `@return`：非 `void` 且非建構子方法應提供。
- `@throws`（或 `@exception`）：說明拋出條件與語意。
- 建議核心順序：`@param` -> `@return` -> `@throws`。

## 3) 語意規範

- 摘要句應描述行為，不可只是重述方法名稱。
- `@param` 應描述用途與限制，不是重複參數名稱。
- `@return` 應描述回傳語意，不是模板句。
- `@throws` 應描述觸發條件。

## 4) inline tags

- 使用 `{@code ...}` 呈現程式碼片段。
- 需要交叉參照時使用 `{@link ...}`。

## 5) 實作建議（此 skill 採用）

- Lint 階段檢查：
  - 摘要句存在且非空
  - block tag 順序
  - `@param/@return/@throws` 結構完整性
  - `void`/建構子不可出現 `@return`
  - 已宣告 `throws` 需有對應 `@throws`
