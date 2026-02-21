import { t } from "./i18n";
import { HIGH_USAGE_THRESHOLD } from "./types";
import {
  formatDuration,
  createProgressBar,
  calcRemainPercent,
  formatTokens,
  fetchWithTimeout,
  safeMax,
  maskString,
} from "./utils";
import type { ZhipuAuthNode, QueryResult } from "./types";

const ZHIPU_QUOTA_QUERY_URL = "https://bigmodel.cn/api/monitor/usage/quota/limit";
const ZAI_QUOTA_QUERY_URL = "https://api.z.ai/api/monitor/usage/quota/limit";

interface ZhipuUsageResponse {
  success: boolean;
  code: number;
  msg?: string;
  data: {
    limits: Array<{
      type: string;
      usage: number;
      currentValue: number;
      percentage: number;
      nextResetTime?: number;
    }>;
  };
}

async function fetchUsage(apiKey: string, apiUrl: string): Promise<ZhipuUsageResponse> {
  const response = await fetchWithTimeout(apiUrl, {
    method: "GET",
    headers: {
      Authorization: apiKey,
      "Content-Type": "application/json",
      "User-Agent": "OpenCode-Status-Plugin/1.0",
    },
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API request failed (${response.status}): ${errorText}`);
  }
  const data = (await response.json()) as ZhipuUsageResponse;
  if (!data.success || data.code !== 200) {
    throw new Error(`API error (${data.code}): ${data.msg || "Unknown error"}`);
  }
  return data;
}

function formatZhipuUsage(data: ZhipuUsageResponse, apiKey: string, accountLabel: string): string {
  const lines: string[] = [];
  const limits = data.data.limits;
  const maskedKey = maskString(apiKey);
  lines.push(`${t.account}        ${maskedKey} (${accountLabel})`);
  lines.push("");

  if (!limits || limits.length === 0) {
    lines.push(t.noQuotaData);
    return lines.join("\n");
  }

  const tokensLimit = limits.find((l) => l.type === "TOKENS_LIMIT");
  if (tokensLimit) {
    const remainPercent = calcRemainPercent(tokensLimit.percentage);
    const progressBar = createProgressBar(remainPercent);
    lines.push(t.zhipuTokensLimit);
    lines.push(`${progressBar} ${t.remaining(remainPercent)}`);
    lines.push(`${t.used}: ${formatTokens(tokensLimit.currentValue)} / ${formatTokens(tokensLimit.usage)}`);
    if (tokensLimit.nextResetTime) {
      const resetSeconds = Math.max(0, Math.floor((tokensLimit.nextResetTime - Date.now()) / 1000));
      lines.push(t.resetIn(formatDuration(resetSeconds)));
    }
  }

  const timeLimit = limits.find((l) => l.type === "TIME_LIMIT");
  if (timeLimit) {
    if (tokensLimit) lines.push("");
    const remainPercent = calcRemainPercent(timeLimit.percentage);
    const progressBar = createProgressBar(remainPercent);
    lines.push(t.zhipuMcpLimit);
    lines.push(`${progressBar} ${t.remaining(remainPercent)}`);
    lines.push(`${t.used}: ${timeLimit.currentValue} / ${timeLimit.usage}`);
  }

  const maxPercentage = safeMax(limits.map((l) => l.percentage));
  if (maxPercentage >= HIGH_USAGE_THRESHOLD) {
    lines.push("");
    lines.push(t.limitReached);
  }

  return lines.join("\n");
}

async function queryUsage(
  authData: ZhipuAuthNode | undefined,
  apiUrl: string,
  accountLabel: string,
): Promise<QueryResult | null> {
  if (!authData || authData.type !== "api" || !authData.key) {
    return null;
  }

  try {
    const usage = await fetchUsage(authData.key, apiUrl);
    return {
      success: true,
      output: formatZhipuUsage(usage, authData.key, accountLabel),
    };
  } catch (err) {
    return {
      success: false,
      error: err instanceof Error ? err.message : String(err),
    };
  }
}

export async function queryZhipuUsage(authData: ZhipuAuthNode | undefined): Promise<QueryResult | null> {
  return queryUsage(authData, ZHIPU_QUOTA_QUERY_URL, t.zhipuAccountName);
}

export async function queryZaiUsage(authData: ZhipuAuthNode | undefined): Promise<QueryResult | null> {
  return queryUsage(authData, ZAI_QUOTA_QUERY_URL, t.zaiAccountName);
}
