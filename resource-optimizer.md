📋 創建 OpenCode Skill 指令 (Prompt)

請依照 **OpenCode-AI Standard Skill** 規範，為我建立一個名為 `resource-optimizer` 的 Skill 資料夾與其內部檔案。目標是極大化利用我的 AI 資源，並根據語言環境強制過濾開發垃圾。

核心邏輯要求：

1. **模型分流 (供應商級別，不限版本)**：
   * **情境：重構/架構/Debug** -> 調用 `github-copilot` 供應商（對應我的 $39 Pro+ 額度）。
   * **情境：中文註解/文檔/翻譯** -> 調用 `zhipu` (Z.ai) 供應商。
   * **情境：其餘一般任務** -> 調用 `openai` 供應商。

請產生以下三個檔案的完整內容：

1. `skill.md`

* **名稱**：Resource Optimizer (簡稱 `opt`)。
* **目標**：自動過濾 Java (Maven/Gradle), Python, C#, .NET, C++ 開發垃圾與 IDE 暫存。
* **功能**：根據 Prompt 關鍵字自動切換 Provider，確保高難度任務使用最強模型，簡單任務不浪費進階額度。

2. `script.py` (支援 Python 3.10)

請撰寫 `run(context)` 函數，包含：

* **全環境強制過濾 (Exclusion List)**：
  * **通用/IDE**：`node_modules/`, `dist/`, `build/`, `bin/`, `obj/`, `.git/`, `.env*`, `.idea/`, `.vscode/`, `.settings/`, `*.iml`, `Thumbs.db`, `desktop.ini`
  * **Java**：`.gradle/`, `.mvn/`, `target/`, `**/*.class`, `**/*.jar`, `**/*.war`, `**/*.hprof`
  * **Python**：`__pycache__/`, `*.pyc`, `venv/`, `.venv/`, `.pytest_cache/`
  * **C# / .NET / VS**：`.vs/`, `[Bb]in/`, `[Oo]bj/`, `*.pdb`, `*.suo`, `*.user`, `App_Data/`, `_ReSharper*/`
* **智慧路由 (Provider-Based)**：
  * 若 `context.prompt` 包含 `重構|架構|refactor|architecture|debug|logic` -> 執行 `context.use_provider("github-copilot")` 並設定 `set_context_limit(30000)`。
  * 若 `context.prompt` 包含 `註解|解釋|中文|translate|comment|文檔` -> 執行 `context.use_provider("zhipu")` 並設定 `set_context_limit(8000)`。
  * 其餘任務 -> 執行 `context.use_provider("openai")` 並設定 `set_context_limit(15000)`。
* **檔案保護**：使用 `on_before_read` 鉤子，自動跳過 `file.size > 500000` (500KB) 的檔案。

3. `reference.json`

* **Runtime**: `python`
* **Entry**: `script.py`
* **Commands**: `["opt", "resource-optimizer"]`
* **Permissions**: `["read_project", "change_model", "exclude_files"]`
