# Python Docstring 風格指南（zh-TW）

本文件提供 Python 文件字串的實務規則，並對齊 `pep257`（官方）與 `google`（Google Style）兩種風格。

## 1) 摘要首句規則

- 第一行用一句話說明「做什麼」與「何時使用」。
- 避免只把函式名稱改寫成句子。
- 避免無資訊句型（例如：執行某功能）。

## 2) 參數說明

- 說明參數角色與用途，不要只重複參數名稱。
- 能指出單位時需明確（毫秒、秒、筆數）。

## 3) 回傳說明

- `bool`: 說明判斷條件。
- 集合型別：說明集合內容。
- 物件型別：說明語意而非只列型別名稱。

## 4) 例外說明

- 明確描述拋出條件。

## 5) 非同步語意

- `async def` 應描述 await 後的完成語意。
- 若可能拋出特定例外，需在文件中說明。

## 6) 格式建議

- PEP 257：可搭配 reST 標記（`:param` / `:returns` / `:raises`）。
- Google Style：使用 `Args` / `Returns` / `Raises` 區段。
- 同一專案應固定單一格式，不要混用。

## 7) 避免事項

- 不使用 emoji。
- 不使用「輸入參數」「操作結果」等模板語句。
- 不寫與程式行為不一致的說明。

## 8) Google Style 參考範本

```python
def calculate_metrics(data: list[float], threshold: float = 0.5) -> dict:
    """計算資料集的性能指標。

    這裡可以寫詳細描述，解釋演算法原理、注意事項或使用場景。

    Args:
        data: 輸入的浮點數列表，代表原始樣本。
        threshold: 判定門檻值，預設為 0.5。

    Returns:
        包含 accuracy 與 f1_score 的字典。

    Raises:
        ValueError: 當 data 為空列表時拋出。

    Examples:
        >>> calculate_metrics([0.1, 0.9], threshold=0.4)
        {'accuracy': 0.8, 'f1_score': 0.75}
    """
```
