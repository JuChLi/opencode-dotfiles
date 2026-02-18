# 高品質 Javadoc 檢查清單

提交前請逐項確認：

## 覆蓋率

- [ ] 所有 `public/protected` 類別、介面、列舉都有 Javadoc。
- [ ] 所有 `public/protected` 方法都有 Javadoc。
- [ ] 若專案需要，`private` 方法也有一致標準。

## Standard Doclet 核心規範

- [ ] 摘要句非空，且位於主描述第一段。
- [ ] block tags 位於主描述後方，並有清楚分段。
- [ ] 核心 tag 順序為 `@param` -> `@return` -> `@throws`。
- [ ] 若使用 Google 風格，`@deprecated` 位於 `@throws` 之後。
- [ ] 每個方法參數都有對應 `@param`。
- [ ] 非 `void` 且非建構子有 `@return`。
- [ ] `void`/建構子沒有 `@return`。
- [ ] 宣告 `throws` 的例外有對應 `@throws` 說明。
- [ ] 核心 tags（`@param/@return/@throws/@deprecated`）沒有空白描述。

## 語意正確性

- [ ] 摘要首句與方法實際行為一致。
- [ ] 若使用 Google 風格，摘要符合 summary fragment（避免 `This method...` / 「此方法...」）。
- [ ] `@param` 描述參數用途，而不是重複參數名稱。
- [ ] `@return` 反映真實回傳語意。
- [ ] `@throws` 反映真實拋出條件。
- [ ] 若使用 `@deprecated`，已描述棄用原因與替代 API（建議 `{@link ...}`）。

## 非同步與 Reactive 語意

- [ ] `Future` 方法描述成功完成與失敗完成語意。
- [ ] Verticle `start/stop` 明確描述 Promise 的完成時機。
- [ ] 不誤導事件迴圈（例如寫成同步阻塞）。

## 語言品質（zh-TW）

- [ ] 使用台灣繁體中文。
- [ ] 不使用 emoji 與裝飾符號。
- [ ] 避免模板句（例如「操作結果」「輸入參數」「執行某操作」）。

## 一致性

- [ ] 同類型方法（`get/is/set`）描述風格一致。
- [ ] 同一模組術語一致（例如資料點、來源、通知、觀測）。
- [ ] 文件更新與程式碼更新同步。

## 風格可追溯性

- [ ] 已確認符合 `Documentation Comment Specification for the Standard Doclet`。
- [ ] 已記錄目前使用的風格設定檔（`vertx/apache/custom`）。
- [ ] 若使用 custom style，已保存來源 URL 或文件路徑。
- [ ] custom style 規則可由腳本重現（不是僅靠人工記憶）。
