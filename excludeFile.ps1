# 1. 定義全域忽略檔路徑
$GlobalIgnorePath = "$HOME\.opencode_global_ignore"

# 2. 針對你的開發環境 (Java, Python, C#, .NET) 定義內容
$IgnoreContent = @"
# --- [通用] 額度殺手 ---
node_modules/
dist/
build/
out/
target/
bin/
obj/
vendor/

# --- [Java / Maven / Gradle] ---
.gradle/
.mvn/
*.class
*.jar
*.war
*.ear
*.hprof
*.log

# --- [Python] ---
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
.pytest_cache/

# --- [C# / .NET / VS 2019] ---
.vs/
[Bb]in/
[Oo]bj/
*.user
*.userosscache
*.sln.doccache
*.suo
*.pdb
App_Data/
packages/
_ReSharper*/

# --- [IDE 設定 (IntelliJ, Eclipse, VS Code)] ---
.idea/
*.iml
.settings/
.classpath
.project
.vscode/
.history/

# --- [系統與大型檔案] ---
.git/
.env
*.sqlite
*.db
*.zip
*.tar
*.gz
*.exe
*.dll
.DS_Store
Thumbs.db
desktop.ini
\$RECYCLE.BIN/
"@

Set-Content -Path $GlobalIgnorePath -Value $IgnoreContent
[Environment]::SetEnvironmentVariable("OPENCODE_IGNORE_PATH", $GlobalIgnorePath, "User")

Write-Host "✅ 全域忽略檔已更新，支援 Java/Python/C#！" -ForegroundColor Green
Write-Host "🚀 請重啟終端機以生效。" -ForegroundColor Cyan
