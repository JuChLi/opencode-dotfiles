/**
 * i18n (zh-TW + en)
 */
export type Language = "zh-TW" | "en";

function detectLanguage(): Language {
  try {
    const intlLocale = Intl.DateTimeFormat().resolvedOptions().locale;
    if (intlLocale.startsWith("zh")) return "zh-TW";
  } catch {
    // ignore
  }
  const lang = process.env.LANG || process.env.LC_ALL || process.env.LANGUAGE || "";
  if (lang.startsWith("zh")) return "zh-TW";
  return "en";
}

const translations = {
  "zh-TW": {
    // time
    days: (n: number) => `${n}天`,
    hours: (n: number) => `${n}小時`,
    minutes: (n: number) => `${n}分鐘`,

    // quota
    hourLimit: (h: number) => `${h}小時限額`,
    remaining: (p: number) => `剩餘 ${p}%`,
    resetIn: (t: string) => `重置：${t}後`,

    // generic
    account: "帳號：",
    plan: "方案：",
    used: "已用",
    unknown: "未知",

    // errors
    authError: (path: string, err: string) => `❌ 無法讀取認證檔：${path}\n錯誤：${err}`,
    minimaxApiError: (status: number, text: string) => `MiniMax API 請求失敗 (${status}): ${text}`,
    timeoutError: (seconds: number) => `請求逾時 (${seconds}秒)`,
    noAccounts:
      "找不到已設定的 MiniMax 帳號資訊。\n\n" +
      "請先在 OpenCode 內用 /connect（或等效流程）設定 MiniMax，讓它寫入 auth.json。\n" +
      "支援節點：minimax-coding-plan / minimax",

    // titles
    minimaxTitle: "## MiniMax 帳號配額",

    // labels
    promptsLimit5h: "5 小時 Prompt 限額",
    noQuotaData: "目前沒有配額資料",
  },
  en: {
    days: (n: number) => `${n}d`,
    hours: (n: number) => `${n}h`,
    minutes: (n: number) => `${n}m`,

    hourLimit: (h: number) => `${h}-hour limit`,
    remaining: (p: number) => `${p}% remaining`,
    resetIn: (t: string) => `Resets in: ${t}`,

    account: "Account:",
    plan: "Plan:",
    used: "Used",
    unknown: "unknown",

    authError: (path: string, err: string) => `❌ Failed to read auth file: ${path}\nError: ${err}`,
    minimaxApiError: (status: number, text: string) => `MiniMax API request failed (${status}): ${text}`,
    timeoutError: (seconds: number) => `Request timeout (${seconds}s)`,
    noAccounts:
      "No MiniMax auth found.\n\n" +
      "Please configure MiniMax in OpenCode (/connect or equivalent) so it writes auth.json.\n" +
      "Supported nodes: minimax-coding-plan / minimax",

    minimaxTitle: "## MiniMax Account Quota",
    promptsLimit5h: "5-hour prompt limit",
    noQuotaData: "No quota data available",
  },
} as const;

export const currentLang: Language = detectLanguage();
export const t = translations[currentLang];
