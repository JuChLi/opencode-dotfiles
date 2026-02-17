# Vert.x Javadoc 風格指南（台灣繁體中文）

本文件定義 Java + Vert.x 專案的 Javadoc 撰寫慣例，用於統一語氣、術語與非同步語意描述。

本指南建立在 Standard Doclet 官方規範之上：

- 先符合 `Documentation Comment Specification for the Standard Doclet`
- 再套用 Vert.x 專案語氣與術語偏好

## 1) 摘要首句規則

- 第一行用一句話說明「方法做什麼」以及「在什麼情境下使用」。
- 避免只把方法名稱翻成句子。
- 避免無資訊句型（例如：執行某操作）。

## 2) 非同步完成語意（Future）

對回傳 `Future<T>` 的方法，`@return` 應描述完成語意：

- 成功完成時回傳什麼
- 失敗完成時如何傳遞錯誤（failed future / exception）

範例：

```java
/**
 * 觸發一次資料收集流程，並在完成後回傳收集結果。
 *
 * @return 非同步收集結果；失敗時回傳 failed future。
 */
Future<CollectionResult> collectData();
```

## 3) `@param` 規則

- 說明參數的「角色」與「用途」，不要只寫「輸入參數」。
- 能指出單位時要明確（毫秒、秒、筆數）。

範例：

```java
@param timeoutMs 請求逾時時間（毫秒）。
@param sourceId 資料來源識別碼。
```

## 4) `@return` 規則

- `boolean`: 說明判斷條件。
- 集合型別：說明集合內容。
- Value Object：說明語意而非型別名稱。

範例：

```java
@return 當資料點符合 OGC 條件時回傳 true。
```

## 5) `@throws` 規則

- 明確描述拋出例外的觸發條件。

範例：

```java
@throws IllegalArgumentException 當設定值格式不合法時拋出。
```

## 6) Verticle 方法語意建議

- `start(Promise<Void>)`：說明啟動流程與完成條件。
- `stop(Promise<Void>)`：說明停止流程與資源釋放。

## 7) 避免事項

- 不使用 emoji。
- 不使用「操作結果」「參數 xxx」等模板語句。
- 不寫與程式行為不一致的說明。

## 8) 與其他風格切換

- 若使用 `apache` 或 custom profile，請保持本文件的「語意正確性」原則不變。
- 可調整句型風格，但不可降低資訊量。
