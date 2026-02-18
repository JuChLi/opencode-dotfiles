# 風格來源發現流程

當你要建立或更新 style profile，請依下列順序找來源並保留可追溯性。

## 參考層級

1. 專案內規範（最高優先）
   - 例如：`CONTRIBUTING.md`、`docs/style-guide.md`、團隊 ADR。
2. Google developer documentation style
   - 入口：<https://developers.google.com/style>
3. 業界通用框架
   - Diataxis：<https://diataxis.fr/>
   - Write the Docs 原則：<https://www.writethedocs.org/guide/writing/docs-principles/>

## 建議流程

1. 先找專案內是否已有強制規範。
2. 無明確規範時，採 `google-zhtw` 作為預設。
3. 若文件場景偏交接，改用 `handoff-zhtw`。
4. 若有額外需求，用 `extract_style_profile.py` 產生 custom profile 草稿。
5. 人工審核 custom profile，刪除不適用規則，再納入版本控管。

## 最小可追溯資訊

每個 style profile 至少保留：

- `source`：來源 URL 或檔案路徑。
- `generatedAt`：產生時間（若由腳本產生）。
- `extends`：繼承自哪個 baseline。
- `notes`：手動調整理由與限制。

## 常見錯誤

- 只套規範名稱，沒有對應來源 URL。
- 多份文件各用一套規則，未定義優先序。
- 把非官方部落格建議視為唯一準則。
