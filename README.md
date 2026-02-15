# OpenCode Config - 個人 OpenCode 設定

這是我的個人 OpenCode 全域設定，包含自訂指令和設定檔。

## 快速安裝

在新電腦的 OpenCode 中輸入：

```
請幫我從 https://github.com/JuChLi/opencode-config 下載並安裝我的 OpenCode 指令
```

或手動安裝：

```bash
# Clone repo
git clone https://github.com/JuChLi/opencode-config.git ~/opencode-config-temp

# 執行安裝
cd ~/opencode-config-temp
./install.sh        # Linux/macOS/Git Bash
# 或
.\install.ps1       # Windows PowerShell

# 清理
rm -rf ~/opencode-config-temp
```

## 包含指令

| 指令 | 說明 |
|------|------|
| `/load` | 讀取專案進度（如同讀取遊戲存檔） |
| `/status` | 讀取專案進度（/load 的別名） |
| `/save` | 儲存專案進度到 SESSION.md |

## 使用流程

```
# 開始工作時 - 讀取進度
/load

# 結束工作前 - 儲存進度
/save
```

## 目錄結構

```
opencode-config/
├── README.md         # 本說明文件
├── install.sh        # Linux/macOS 安裝腳本
├── install.ps1       # Windows PowerShell 安裝腳本
└── commands/         # 自訂指令
    ├── load.md
    ├── status.md
    └── save.md
```

## 新增指令

1. 在 `commands/` 目錄新增 `.md` 檔案
2. Push 到 GitHub
3. 在其他電腦重新執行安裝腳本
