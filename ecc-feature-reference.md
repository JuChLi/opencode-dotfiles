---
doc_type: reference
style: google-zhtw
source_repo: https://github.com/affaan-m/everything-claude-code
verified_at: 2026-02-18
---

# Everything Claude Code 功能參考

## 範圍

本文件整理 `affaan-m/everything-claude-code`（以下簡稱 ECC）在主分支可見的功能，重點放在「你可直接採用的能力」與「每項能力的用途」。

納入範圍如下：

- Claude Code plugin 組件（agents、commands、skills、rules、hooks、MCP 設定）。
- OpenCode 對應組件（`.opencode/opencode.json`、plugins、tools、commands、instructions）。
- 測試與維運相關組件（`scripts/ci`、`tests`、`examples`、`contexts`）。

不納入範圍如下：

- 第三方服務本身的內部實作（例如 GitHub App、AgentShield 內部規則引擎）。
- 專案外部平台的商業方案內容。

## 名詞與定義

| 名詞 | 定義 |
|---|---|
| Agent | 針對特定任務的子代理，負責規劃、審查、修復、測試等專職工作。 |
| Command | 以 `/command` 方式觸發的工作流入口，通常會委派到指定 agent。 |
| Skill | 任務知識包與流程規範，提供「何時用、怎麼做、怎麼驗證」。 |
| Rule | 長期遵循的專案規範，例如安全、測試覆蓋率、git 流程。 |
| Hook | Claude Code 的事件觸發自動化（`PreToolUse`、`PostToolUse`、`SessionEnd` 等）。 |
| Plugin Event | OpenCode 的事件系統（例如 `tool.execute.before`、`file.edited`），可模擬 hook 行為。 |
| MCP | Model Context Protocol 伺服器設定，擴充工具能力。 |
| Instinct | `continuous-learning-v2` 的可學習模式片段，可匯入、匯出、聚類。 |

## 規格

### 功能矩陣總覽

| 類別 | 數量 | 主要用途 |
|---|---:|---|
| Agents | 13 | 專職分工（規劃、審查、安全、測試、修復、文件、資料庫）。 |
| Commands | 31 | 把常見開發流程做成可重用指令。 |
| Skills | 43 | 領域知識與工作流模板。 |
| Rules | 23 | `common` + 語言特化（TypeScript、Python、Go）。 |
| Claude Hooks 階段 | 6 | 以事件觸發提醒、阻擋與自動檢查。 |
| OpenCode Plugin Events（已用） | 9 | 用 plugin 事件取代 hooks.json 型態自動化。 |
| OpenCode Custom Tools | 3 | 測試、覆蓋率、安全掃描。 |

### Agents（13）

| Agent | 主要用途 | 典型情境 |
|---|---|---|
| `planner` | 實作規劃與拆解。 | 新功能、跨模組重構、任務分階段。 |
| `architect` | 系統設計與技術決策。 | 架構調整、可擴展性設計。 |
| `tdd-guide` | TDD 流程執行與覆蓋率要求。 | 先測後寫、修 bug、重構驗證。 |
| `code-reviewer` | 程式碼品質與可維護性審查。 | 變更完成後的品質把關。 |
| `security-reviewer` | 安全漏洞檢查與修補建議。 | 認證授權、輸入處理、敏感資料流程。 |
| `build-error-resolver` | Build / 型別錯誤的最小修補。 | CI fail、TypeScript 編譯失敗。 |
| `e2e-runner` | E2E 測試建立與執行。 | 重要使用流程驗證。 |
| `refactor-cleaner` | 死碼清理與重複邏輯整併。 | 技術債整理、刪除未使用程式。 |
| `doc-updater` | 文件與 codemap 同步更新。 | 功能改動後文件補齊。 |
| `go-reviewer` | Go 程式碼審查。 | Go 專案風格、併發與效能檢查。 |
| `go-build-resolver` | Go build / vet 問題修復。 | Go 專案建置失敗。 |
| `python-reviewer` | Python 程式碼審查。 | PEP 8、型別註記、安全檢查。 |
| `database-reviewer` | 資料庫與 SQL 優化。 | Schema 設計、查詢效能、Supabase 最佳化。 |

### Commands（31）

| Command | 主要用途 |
|---|---|
| `/plan` | 建立實作計畫與風險拆解。 |
| `/tdd` | 執行測試先行開發流程。 |
| `/code-review` | 檢視變更品質與風險。 |
| `/build-fix` | 修復建置與型別錯誤。 |
| `/e2e` | 產生並執行端到端測試。 |
| `/refactor-clean` | 移除死碼與清理重複邏輯。 |
| `/learn` | 從當前工作階段萃取可重用模式。 |
| `/checkpoint` | 保存驗證狀態與里程碑。 |
| `/verify` | 執行驗證迴圈。 |
| `/eval` | 依評估條件打分與比對。 |
| `/test-coverage` | 分析測試覆蓋率。 |
| `/update-docs` | 更新說明文件。 |
| `/update-codemaps` | 更新程式碼地圖。 |
| `/setup-pm` | 設定套件管理器。 |
| `/orchestrate` | 多代理協作流程。 |
| `/go-review` | Go 專案審查流程。 |
| `/go-test` | Go TDD 流程。 |
| `/go-build` | Go build 錯誤修復。 |
| `/python-review` | Python 程式碼審查。 |
| `/skill-create` | 從 git 歷史產生技能草稿。 |
| `/instinct-status` | 檢視學習到的 instincts。 |
| `/instinct-import` | 匯入 instincts。 |
| `/instinct-export` | 匯出 instincts。 |
| `/evolve` | 將 instincts 聚類成技能。 |
| `/sessions` | 管理工作階段歷史。 |
| `/pm2` | 產生 PM2 服務生命週期操作。 |
| `/multi-plan` | 多代理任務拆解。 |
| `/multi-execute` | 多代理協同執行。 |
| `/multi-backend` | 後端多服務協作流程。 |
| `/multi-frontend` | 前端多服務協作流程。 |
| `/multi-workflow` | 通用多服務工作流編排。 |

### Skills（43）

| Skill | 主要用途 |
|---|---|
| `coding-standards` | 語言層級最佳實務。 |
| `clickhouse-io` | ClickHouse 分析查詢與資料工程。 |
| `backend-patterns` | API、資料庫、快取模式。 |
| `frontend-patterns` | React / Next.js 實作模式。 |
| `continuous-learning` | 從工作階段自動萃取模式。 |
| `continuous-learning-v2` | 以信心分數管理 instincts。 |
| `iterative-retrieval` | 子代理漸進式上下文收斂。 |
| `strategic-compact` | 手動 compact 時機建議。 |
| `tdd-workflow` | TDD 方法論。 |
| `security-review` | 安全檢查清單。 |
| `eval-harness` | 驗證迴圈評估框架。 |
| `verification-loop` | 持續驗證流程。 |
| `golang-patterns` | Go 慣用寫法與設計模式。 |
| `golang-testing` | Go 測試、TDD、benchmark。 |
| `cpp-coding-standards` | C++ Core Guidelines 風格準則。 |
| `cpp-testing` | C++ 測試（GoogleTest、CMake/CTest）。 |
| `django-patterns` | Django 模型與視圖模式。 |
| `django-security` | Django 安全實務。 |
| `django-tdd` | Django TDD 流程。 |
| `django-verification` | Django 驗證迴圈。 |
| `python-patterns` | Python 慣用模式。 |
| `python-testing` | pytest 測試實務。 |
| `springboot-patterns` | Spring Boot 設計模式。 |
| `springboot-security` | Spring Boot 安全實務。 |
| `springboot-tdd` | Spring Boot TDD。 |
| `springboot-verification` | Spring Boot 驗證流程。 |
| `configure-ecc` | 互動式安裝精靈。 |
| `security-scan` | AgentShield 安全掃描整合。 |
| `java-coding-standards` | Java 程式設計準則。 |
| `jpa-patterns` | JPA / Hibernate 模式。 |
| `postgres-patterns` | PostgreSQL 優化模式。 |
| `nutrient-document-processing` | Nutrient API 文件處理流程。 |
| `project-guidelines-example` | 專案級技能模板。 |
| `database-migrations` | Prisma/Drizzle/Django/Go 遷移模式。 |
| `api-design` | REST API 設計與分頁、錯誤格式。 |
| `deployment-patterns` | CI/CD、健康檢查、回滾流程。 |
| `docker-patterns` | Docker Compose、網路、Volume、安全。 |
| `e2e-testing` | Playwright E2E 與 Page Object 模式。 |
| `content-hash-cache-pattern` | SHA-256 內容雜湊快取模式。 |
| `cost-aware-llm-pipeline` | LLM 成本與路由優化。 |
| `regex-vs-llm-structured-text` | Regex 與 LLM 解析策略選擇。 |
| `swift-actor-persistence` | Swift actor 持久化模式。 |
| `swift-protocol-di-testing` | Swift 協定式依賴注入與測試。 |

### Rules 與規範層（23 份）

| 層級 | 檔案數 | 內容重點 |
|---|---:|---|
| `rules/common/` | 8 | 通用規範：coding-style、git-workflow、testing、performance、patterns、hooks、agents、security。 |
| `rules/typescript/` | 5 | TypeScript/JavaScript 專屬 coding-style、hooks、patterns、security、testing。 |
| `rules/python/` | 5 | Python 專屬 coding-style、hooks、patterns、security、testing。 |
| `rules/golang/` | 5 | Go 專屬 coding-style、hooks、patterns、security、testing。 |

> 語言層規範會延伸 `common`，安裝時需保留目錄結構，不建議扁平化複製。

### Hooks 與事件自動化

#### Claude Code hooks（`hooks/hooks.json`）

| 階段 | 主要行為 |
|---|---|
| `PreToolUse` | 阻擋非 tmux dev server、提醒長任務使用 tmux、push 前提醒、阻擋零散 md 檔建立、建議 compact。 |
| `PreCompact` | compact 前先保存狀態。 |
| `SessionStart` | 載入先前脈絡並偵測套件管理器。 |
| `PostToolUse` | PR 建立後提示審查指令、建置完成異步分析、編輯後格式化/型別檢查/console.log 警示。 |
| `Stop` | 回應結束後檢查已修改檔案中的 `console.log`。 |
| `SessionEnd` | 結束時保存狀態並執行模式萃取。 |

#### OpenCode plugin events（以 plugin 事件模擬 hooks）

| OpenCode 事件 | 主要行為 |
|---|---|
| `tool.execute.before` | push 前提醒、文件建立警示、長任務執行提醒。 |
| `tool.execute.after` | TypeScript 檢查、PR 建立紀錄。 |
| `file.edited` | 自動格式化、`console.log` 掃描。 |
| `session.created` | 啟用訊息與初始脈絡檢查。 |
| `session.idle` | 任務完成審計與通知。 |
| `session.deleted` | 清理 session 內狀態。 |
| `file.watcher.updated` | 追蹤變更檔案。 |
| `permission.asked` | 記錄權限請求。 |
| `todo.updated` | 輸出進度統計。 |

#### Claude 與 OpenCode 事件對照

| Claude Code | OpenCode |
|---|---|
| `PreToolUse` | `tool.execute.before` |
| `PostToolUse` | `tool.execute.after` |
| `Stop` | `session.idle` |
| `SessionStart` | `session.created` |
| `SessionEnd` | `session.deleted` |

### OpenCode Custom Tools（3）

| Tool | 用途 | 輸出重點 |
|---|---|---|
| `run-tests` | 偵測套件管理器與測試框架，組合測試命令。 | 回傳建議執行命令（可含 coverage、watch、pattern）。 |
| `check-coverage` | 讀取 coverage 報告並比對門檻。 | 回傳總覆蓋率、低覆蓋檔案、改進建議。 |
| `security-audit` | 依賴漏洞、秘密字串與程式碼反模式掃描。 | 回傳檢查摘要、發現項與修正建議。 |

### 測試與維運資產

| 類別 | 內容 |
|---|---|
| CI 驗證腳本 | `scripts/ci/validate-*.js` 驗證 agents、commands、hooks、rules、skills。 |
| 共享函式庫 | `scripts/lib` 提供 package manager、session manager、utils。 |
| 測試套件 | `tests/lib`、`tests/hooks`、`tests/integration`、`tests/ci`。 |
| contexts | `contexts/dev.md`、`contexts/review.md`、`contexts/research.md`。 |
| examples | 多個 `CLAUDE.md` 範例與 session 配置樣板。 |
| MCP 設定 | `mcp-configs/mcp-servers.json` 提供常見服務連線模板。 |

### 生態系延伸能力

| 能力 | 用途 |
|---|---|
| Skill Creator | 從 git 歷史自動萃取技能與 instincts。 |
| AgentShield | 安全掃描工具（可 CLI 與 CI 整合）。 |
| Cursor 支援 | 提供 `.cursor/` 轉換版組件（部分命令為 stub）。 |
| OpenCode 支援 | 提供 `.opencode/` 組件，含 plugin 事件與 custom tools。 |

## 約束與限制

- Claude Code plugin 無法自動分發 `rules/`，需手動安裝。
- Claude Code v2.1+ 會自動載入 `hooks/hooks.json`，`plugin.json` 不應再重複宣告 `hooks` 欄位。
- OpenCode 不支援 Claude 的 `hooks/hooks.json` 格式；需改用 plugin events。
- OpenCode 功能覆蓋度與 Claude Code 不完全一致，特別是 command/skill 數量會有差異。
- 多項功能依賴外部工具（例如 `prettier`、`tsc`、`tmux`、`pm2`、`gh`、`npm audit`），缺少時會降級或失效。
- README、`.opencode`、`MIGRATION` 之間偶爾會有版本或數量描述落差，採用前建議以實際檔案清單再確認一次。

## 錯誤與例外

| 情境 | 常見訊息 | 主要原因 | 建議處理 |
|---|---|---|---|
| plugin hooks 重複 | `Duplicate hooks file detected` | plugin 清單重複宣告 hooks 檔。 | 從 `plugin.json` 移除 hooks 欄位。 |
| plugin 驗證失敗 | `agents: Invalid input` | `agents` 欄位使用目錄字串或非陣列格式。 | 改為明確檔案路徑陣列。 |
| 覆蓋率工具無結果 | `No coverage report found` | 尚未產生 coverage JSON。 | 先執行含 coverage 的測試。 |
| 格式化或型別檢查未生效 | 無明確錯誤或僅 warning | 環境缺少 `prettier` 或 `tsc`。 | 安裝對應工具並納入專案 scripts。 |
| OpenCode plugin 無法載入 | 指令或事件未觸發 | plugin 路徑或匯出設定錯誤。 | 檢查 `plugin` 欄位與 `index.ts` 匯出。 |

## 版本與相容性

| 版本 | 變更重點 |
|---|---|
| v1.4.1（2026-02） | 修正 instinct import 內容遺失問題。 |
| v1.4.0（2026-02） | 多語言 rules 架構、安裝精靈、PM2 與 multi-* 指令。 |
| v1.3.0（2026-02） | OpenCode plugin 支援與 custom tools。 |
| v1.2.0（2026-02） | Python/Django、Spring Boot、continuous-learning-v2。 |

相容性重點：

- Claude Code CLI 建議 `v2.1.0` 以上。
- OpenCode 需以 `.opencode/opencode.json` 載入配置。
- Cursor 採轉換版設定，命令與 hooks 支援度和 Claude/OpenCode 不同。

## 相關連結

- 專案首頁：`https://github.com/affaan-m/everything-claude-code`
- 主要說明：`https://raw.githubusercontent.com/affaan-m/everything-claude-code/main/README.md`
- Claude plugin 清單：`https://raw.githubusercontent.com/affaan-m/everything-claude-code/main/.claude-plugin/plugin.json`
- OpenCode 設定：`https://raw.githubusercontent.com/affaan-m/everything-claude-code/main/.opencode/opencode.json`
- OpenCode README：`https://raw.githubusercontent.com/affaan-m/everything-claude-code/main/.opencode/README.md`
- OpenCode 遷移指南：`https://raw.githubusercontent.com/affaan-m/everything-claude-code/main/.opencode/MIGRATION.md`
- Hooks 設定：`https://raw.githubusercontent.com/affaan-m/everything-claude-code/main/hooks/hooks.json`
- Rules 說明：`https://raw.githubusercontent.com/affaan-m/everything-claude-code/main/rules/README.md`
