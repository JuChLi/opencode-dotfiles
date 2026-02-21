import * as fs from "fs";
import * as path from "path";
import * as os from "os";
import { t } from "./i18n";
import { createProgressBar, fetchWithTimeout } from "./utils";
import type { CopilotAuthNode, QueryResult } from "./types";

const GITHUB_API_BASE_URL = "https://api.github.com";
const COPILOT_QUOTA_CONFIG_PATH = path.join(os.homedir(), ".config", "opencode", "copilot-quota-token.json");
const COPILOT_VERSION = "0.35.0";
const EDITOR_VERSION = "vscode/1.107.0";
const EDITOR_PLUGIN_VERSION = `copilot-chat/${COPILOT_VERSION}`;
const USER_AGENT = `GitHubCopilotChat/${COPILOT_VERSION}`;

const COPILOT_HEADERS = {
  "User-Agent": USER_AGENT,
  "Editor-Version": EDITOR_VERSION,
  "Editor-Plugin-Version": EDITOR_PLUGIN_VERSION,
  "Copilot-Integration-Id": "vscode-chat",
};

interface QuotaConfig {
  token: string;
  username: string;
  tier: string;
}

function readQuotaConfig(): QuotaConfig | null {
  try {
    if (!fs.existsSync(COPILOT_QUOTA_CONFIG_PATH)) {
      return null;
    }
    const content = fs.readFileSync(COPILOT_QUOTA_CONFIG_PATH, "utf-8");
    const config = JSON.parse(content);
    if (!config.token || !config.username || !config.tier) {
      return null;
    }
    const validTiers = ["free", "pro", "pro+", "business", "enterprise"];
    if (!validTiers.includes(config.tier)) {
      return null;
    }
    return config;
  } catch {
    return null;
  }
}

async function fetchPublicBillingUsage(config: QuotaConfig) {
  const response = await fetchWithTimeout(
    `${GITHUB_API_BASE_URL}/users/${config.username}/settings/billing/premium_request/usage`,
    {
      headers: {
        Accept: "application/vnd.github+json",
        Authorization: `Bearer ${config.token}`,
        "X-GitHub-Api-Version": "2022-11-28",
      },
    },
  );
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(t.copilotApiError(response.status, errorText));
  }
  return response.json() as Promise<PublicBillingUsage>;
}

async function exchangeForCopilotToken(oauthToken: string): Promise<string | null> {
  try {
    const response = await fetchWithTimeout(`${GITHUB_API_BASE_URL}/copilot_internal/v2/token`, {
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${oauthToken}`,
        ...COPILOT_HEADERS,
      },
    });
    if (!response.ok) {
      return null;
    }
    const tokenData = (await response.json()) as { token: string };
    return tokenData.token;
  } catch {
    return null;
  }
}

function buildGitHubHeaders(token: string) {
  return {
    "Content-Type": "application/json",
    Accept: "application/json",
    Authorization: `Bearer ${token}`,
    ...COPILOT_HEADERS,
  };
}

function buildLegacyHeaders(token: string) {
  return {
    "Content-Type": "application/json",
    Accept: "application/json",
    Authorization: `token ${token}`,
    ...COPILOT_HEADERS,
  };
}

interface CopilotUsageData {
  copilot_plan: string;
  quota_snapshots: {
    premium_interactions?: {
      entitlement: number;
      remaining: number;
      percent_remaining: number;
      unlimited: boolean;
      overage_count: number;
    };
    chat?: {
      entitlement: number;
      remaining: number;
      percent_remaining: number;
      unlimited: boolean;
    };
    completions?: {
      entitlement: number;
      remaining: number;
      percent_remaining: number;
      unlimited: boolean;
    };
  };
  quota_reset_date: string;
}

async function fetchCopilotUsage(authData: CopilotAuthNode): Promise<CopilotUsageData> {
  const oauthToken = authData.refresh || authData.access;
  if (!oauthToken) {
    throw new Error("No OAuth token found in auth data");
  }

  const cachedAccessToken = authData.access;
  const tokenExpiry = authData.expires || 0;

  if (cachedAccessToken && cachedAccessToken !== oauthToken && tokenExpiry > Date.now()) {
    const response = await fetchWithTimeout(`${GITHUB_API_BASE_URL}/copilot_internal/user`, {
      headers: buildGitHubHeaders(cachedAccessToken),
    });
    if (response.ok) {
      return response.json() as Promise<CopilotUsageData>;
    }
  }

  const directResponse = await fetchWithTimeout(`${GITHUB_API_BASE_URL}/copilot_internal/user`, {
    headers: buildLegacyHeaders(oauthToken),
  });
  if (directResponse.ok) {
    return directResponse.json() as Promise<CopilotUsageData>;
  }

  const copilotToken = await exchangeForCopilotToken(oauthToken);
  if (copilotToken) {
    const exchangedResponse = await fetchWithTimeout(`${GITHUB_API_BASE_URL}/copilot_internal/user`, {
      headers: buildGitHubHeaders(copilotToken),
    });
    if (exchangedResponse.ok) {
      return exchangedResponse.json() as Promise<CopilotUsageData>;
    }
    const errorText = await exchangedResponse.text();
    throw new Error(t.copilotApiError(exchangedResponse.status, errorText));
  }

  throw new Error(t.copilotQuotaUnavailable + "\n\n" + t.copilotQuotaWorkaround);
}

interface QuotaInfo {
  entitlement: number;
  remaining: number;
  percent_remaining: number;
  unlimited: boolean;
  overage_count?: number;
}

function formatQuotaLine(name: string, quota: QuotaInfo | undefined, width: number = 20): string {
  if (!quota) return "";
  if (quota.unlimited) {
    return `${name.padEnd(14)} Unlimited`;
  }
  const total = quota.entitlement;
  const used = total - quota.remaining;
  const percentRemaining = Math.round(quota.percent_remaining);
  const progressBar = createProgressBar(percentRemaining, width);
  return `${name.padEnd(14)} ${progressBar} ${percentRemaining}% (${used}/${total})`;
}

function getResetCountdown(resetDate: string): string {
  const reset = new Date(resetDate);
  const now = new Date();
  const diffMs = reset.getTime() - now.getTime();
  if (diffMs <= 0) return t.resetsSoon;
  const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  if (days > 0) {
    return `${days}d ${hours}h`;
  }
  return `${hours}h`;
}

function formatCopilotUsage(data: CopilotUsageData): string {
  const lines: string[] = [];
  lines.push(`${t.account}        GitHub Copilot (${data.copilot_plan})`);
  lines.push("");

  const premium = data.quota_snapshots.premium_interactions;
  if (premium) {
    const premiumLine = formatQuotaLine(t.premiumRequests, premium);
    if (premiumLine) lines.push(premiumLine);
    if (premium.overage_count && premium.overage_count > 0) {
      lines.push(`${t.overage}: ${premium.overage_count} ${t.overageRequests}`);
    }
  }

  const chat = data.quota_snapshots.chat;
  if (chat && !chat.unlimited) {
    const chatLine = formatQuotaLine(t.chatQuota, chat);
    if (chatLine) lines.push(chatLine);
  }

  const completions = data.quota_snapshots.completions;
  if (completions && !completions.unlimited) {
    const completionsLine = formatQuotaLine(t.completionsQuota, completions);
    if (completionsLine) lines.push(completionsLine);
  }

  lines.push("");
  const resetCountdown = getResetCountdown(data.quota_reset_date);
  lines.push(`${t.quotaResets}: ${resetCountdown} (${data.quota_reset_date})`);

  return lines.join("\n");
}

const COPILOT_PLAN_LIMITS: Record<string, number> = {
  free: 50,
  pro: 300,
  "pro+": 1500,
  business: 300,
  enterprise: 1000,
};

interface PublicBillingUsage {
  user: string;
  usageItems: Array<{
    sku: string;
    model?: string;
    grossQuantity: number;
    unitType: string;
  }>;
  timePeriod: {
    year: number;
    month?: number;
  };
}

function formatPublicBillingUsage(data: PublicBillingUsage, tier: string): string {
  const lines: string[] = [];
  lines.push(`${t.account}        GitHub Copilot (@${data.user})`);
  lines.push("");

  const premiumItems = data.usageItems.filter(
    (item) => item.sku === "Copilot Premium Request" || item.sku.includes("Premium"),
  );
  const totalUsed = premiumItems.reduce((sum, item) => sum + item.grossQuantity, 0);
  const limit = COPILOT_PLAN_LIMITS[tier];
  const remaining = Math.max(0, limit - totalUsed);
  const percentRemaining = Math.round((remaining / limit) * 100);
  const progressBar = createProgressBar(percentRemaining, 20);
  lines.push(`${t.premiumRequests.padEnd(14)} ${progressBar} ${percentRemaining}% (${totalUsed}/${limit})`);

  const modelItems = data.usageItems.filter((item) => item.model && item.grossQuantity > 0);
  if (modelItems.length > 0) {
    lines.push("");
    lines.push(t.modelBreakdown);
    const sortedItems = [...modelItems].sort((a, b) => b.grossQuantity - a.grossQuantity);
    for (const item of sortedItems.slice(0, 5)) {
      lines.push(`  ${item.model}: ${item.grossQuantity} ${item.unitType}`);
    }
  }

  lines.push("");
  const period = data.timePeriod;
  const periodStr = period.month ? `${period.year}-${String(period.month).padStart(2, "0")}` : `${period.year}`;
  lines.push(`${t.billingPeriod}: ${periodStr}`);

  return lines.join("\n");
}

export async function queryCopilotUsage(authData: CopilotAuthNode | undefined): Promise<QueryResult | null> {
  const quotaConfig = readQuotaConfig();
  if (quotaConfig) {
    try {
      const billingUsage = await fetchPublicBillingUsage(quotaConfig);
      return {
        success: true,
        output: formatPublicBillingUsage(billingUsage, quotaConfig.tier),
      };
    } catch (err) {
      return {
        success: false,
        error: err instanceof Error ? err.message : String(err),
      };
    }
  }

  if (!authData || authData.type !== "oauth" || !authData.refresh) {
    return {
      success: false,
      error: t.copilotQuotaUnavailable + "\n\n" + t.copilotQuotaWorkaround,
    };
  }

  try {
    const usage = await fetchCopilotUsage(authData);
    return {
      success: true,
      output: formatCopilotUsage(usage),
    };
  } catch (err) {
    return {
      success: false,
      error: err instanceof Error ? err.message : String(err),
    };
  }
}
