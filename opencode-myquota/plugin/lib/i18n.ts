function detectLanguage(): "zh" | "en" {
  try {
    const intlLocale = Intl.DateTimeFormat().resolvedOptions().locale;
    if (intlLocale.startsWith("zh")) return "zh";
  } catch {}
  const lang = process.env.LANG || process.env.LC_ALL || process.env.LANGUAGE || "";
  if (lang.startsWith("zh")) return "zh";
  return "en";
}

const translations = {
  zh: {
    days: (n: number) => `${n}天`,
    hours: (n: number) => `${n}小時`,
    minutes: (n: number) => `${n}分鐘`,
    hourLimit: (h: number) => `${h}小時限額`,
    dayLimit: (d: number) => `${d}天限額`,
    remaining: (p: number) => `剩餘 ${p}%`,
    resetIn: (t: string) => `重置：${t}後`,
    limitReached: "⚠️ 已達到限額上限！",
    account: "帳號：",
    plan: "方案：",
    unknown: "未知",
    used: "已用",
    authError: (path: string, err: string) => `❌ 無法讀取認證檔：${path}\n錯誤：${err}`,
    apiError: (status: number, text: string) => `OpenAI API 請求失敗 (${status}): ${text}`,
    timeoutError: (seconds: number) => `請求逾時 (${seconds}秒)`,
    tokenExpired: "⚠️ OAuth 授權已過期，請在 OpenCode 中使用一次 OpenAI 模型以刷新授權。",
    noAccounts:
      "找不到任何已設定的帳號。\n\n支援的帳號類型：\n- GitHub Copilot\n- OpenAI (Plus/Team/Pro 訂閱)\n- Z.ai (Coding Plan)\n- MiniMax (Coding Plan)",
    queryFailed: "❌ 查詢失敗的帳號：\n",
    openaiTitle: "## OpenAI 帳號額度",
    zhipuTitle: "## 智譜 AI 帳號額度",
    zaiTitle: "## Z.ai 帳號額度",
    minimaxTitle: "## MiniMax 帳號額度",
    copilotTitle: "## GitHub Copilot 帳號額度",
    zhipuApiError: (status: number, text: string) => `智譜 API 請求失敗 (${status}): ${text}`,
    zaiApiError: (status: number, text: string) => `Z.ai API 請求失敗 (${status}): ${text}`,
    minimaxApiError: (status: number, text: string) => `MiniMax API 請求失敗 (${status}): ${text}`,
    zhipuTokensLimit: "5 小時 Token 限額",
    zhipuMcpLimit: "MCP 月度配額",
    zhipuAccountName: "Coding Plan",
    zaiAccountName: "Z.ai",
    minimaxAccountName: "Coding Plan",
    noQuotaData: "目前沒有配額資料",
    promptsLimit5h: "5 小時 Prompt 限額",
    premiumRequests: "Premium",
    chatQuota: "Chat",
    completionsQuota: "Completions",
    overage: "超額使用",
    overageRequests: "次請求",
    quotaResets: "配額重置",
    resetsSoon: "即將重置",
    modelBreakdown: "模型使用明細：",
    billingPeriod: "計費週期",
    copilotApiError: (status: number, text: string) => `GitHub Copilot API 請求失敗 (${status}): ${text}`,
    copilotQuotaUnavailable:
      "⚠️ GitHub Copilot 配額查詢暫時不可用。\n" + "OpenCode 的新 OAuth 整合不支援存取配額 API。",
    copilotQuotaWorkaround:
      "解決方案：\n" +
      "1. 建立一個 fine-grained PAT (https://github.com/settings/tokens?type=beta)\n" +
      "2. 在 'Account permissions' 中將 'Plan' 設為 'Read-only'\n" +
      "3. 建立設定檔 ~/.config/opencode/copilot-quota-token.json:\n" +
      '   {"token": "github_pat_xxx...", "username": "你的使用者名稱"}\n\n' +
      "其他方法：\n" +
      "• 在 VS Code 中點擊狀態列的 Copilot 圖示查看配額\n" +
      "• 訪問 https://github.com/settings/billing 查看使用情況",
  },
  en: {
    days: (n: number) => `${n}d`,
    hours: (n: number) => `${n}h`,
    minutes: (n: number) => `${n}m`,
    hourLimit: (h: number) => `${h}-hour limit`,
    dayLimit: (d: number) => `${d}-day limit`,
    remaining: (p: number) => `${p}% remaining`,
    resetIn: (t: string) => `Resets in: ${t}`,
    limitReached: "⚠️ Rate limit reached!",
    account: "Account:",
    plan: "Plan:",
    unknown: "unknown",
    used: "Used",
    authError: (path: string, err: string) => `❌ Failed to read auth file: ${path}\nError: ${err}`,
    apiError: (status: number, text: string) => `OpenAI API request failed (${status}): ${text}`,
    timeoutError: (seconds: number) => `Request timeout (${seconds}s)`,
    tokenExpired: "⚠️ OAuth token expired. Please use an OpenAI model in OpenCode to refresh authorization.",
    noAccounts:
      "No configured accounts found.\n\nSupported account types:\n- GitHub Copilot\n- OpenAI (Plus/Team/Pro subscribers)\n- Z.ai (Coding Plan)\n- MiniMax (Coding Plan)",
    queryFailed: "❌ Failed to query accounts:\n",
    openaiTitle: "## OpenAI Account Quota",
    zhipuTitle: "## Zhipu AI Account Quota",
    zaiTitle: "## Z.ai Account Quota",
    minimaxTitle: "## MiniMax Account Quota",
    copilotTitle: "## GitHub Copilot Account Quota",
    zhipuApiError: (status: number, text: string) => `Zhipu API request failed (${status}): ${text}`,
    zaiApiError: (status: number, text: string) => `Z.ai API request failed (${status}): ${text}`,
    minimaxApiError: (status: number, text: string) => `MiniMax API request failed (${status}): ${text}`,
    zhipuTokensLimit: "5-hour token limit",
    zhipuMcpLimit: "MCP monthly quota",
    zhipuAccountName: "Coding Plan",
    zaiAccountName: "Z.ai",
    minimaxAccountName: "Coding Plan",
    noQuotaData: "No quota data available",
    promptsLimit5h: "5-hour prompt limit",
    premiumRequests: "Premium",
    chatQuota: "Chat",
    completionsQuota: "Completions",
    overage: "Overage",
    overageRequests: "requests",
    quotaResets: "Quota resets",
    resetsSoon: "Resets soon",
    modelBreakdown: "Model breakdown:",
    billingPeriod: "Period",
    copilotApiError: (status: number, text: string) => `GitHub Copilot API request failed (${status}): ${text}`,
    copilotQuotaUnavailable:
      "⚠️ GitHub Copilot quota query unavailable.\n" + "OpenCode's new OAuth integration doesn't support quota API access.",
    copilotQuotaWorkaround:
      "Solution:\n" +
      "1. Create a fine-grained PAT (https://github.com/settings/tokens?type=beta)\n" +
      "2. Under 'Account permissions', set 'Plan' to 'Read-only'\n" +
      "3. Create config file ~/.config/opencode/copilot-quota-token.json:\n" +
      '   {"token": "github_pat_xxx...", "username": "YourUsername"}\n\n' +
      "Alternatives:\n" +
      "• Click the Copilot icon in VS Code status bar to view quota\n" +
      "• Visit https://github.com/settings/billing for usage info",
  },
};

export type Translations = typeof translations.zh;
export const currentLang: "zh" | "en" = detectLanguage();
export const t = translations[currentLang];
