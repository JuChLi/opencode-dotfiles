import { t } from "./i18n";
import type { QueryResult } from "./types";
import { createProgressBar, fetchWithTimeout, formatDuration, maskString, normalizeRemainsSeconds } from "./utils";
import { extractApiKey, extractGroupId, extractMiniMaxNode } from "./auth";

type MiniMaxRemainsResponse = {
  model_remains?: Array<{
    model_name?: string;
    current_interval_total_count?: number;
    current_interval_usage_count?: number;
    remains_time?: number;
  }>;
};

export async function queryMiniMaxUsageFromAuth(auth: {
  "minimax-coding-plan"?: any;
  minimax?: any;
}): Promise<QueryResult | null> {
  const { node, sourceKey } = extractMiniMaxNode(auth);
  if (!node) {
    return { success: true, output: t.noAccounts };
  }

  const apiKey = extractApiKey(node);
  if (!apiKey) {
    return {
      success: true,
      output:
        `${t.account} ${sourceKey ?? t.unknown}\n` +
        `${t.plan} ${t.unknown}\n\n` +
        "⚠️ 找到 minimax 節點，但缺少 key/api_key/token 欄位。",
    };
  }

  const groupId = extractGroupId(node);
  const baseUrl = "https://www.minimax.io/v1/api/openplatform/coding_plan/remains";
  const url = groupId ? `${baseUrl}?GroupId=${encodeURIComponent(groupId)}` : baseUrl;

  let resp: Response;
  try {
    resp = await fetchWithTimeout(url, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
    });
  } catch (err) {
    return { success: false, error: `MiniMax: ${err instanceof Error ? err.message : String(err)}` };
  }

  if (!resp.ok) {
    const text = await resp.text().catch(() => "");
    if (text.includes("Cloudflare") || text.includes("Attention Required")) {
      return {
        success: true,
        output:
          `${t.account} ${sourceKey ?? t.unknown}\n` +
          `${t.plan} ${t.unknown}\n\n` +
          "⚠️ MiniMax 額度 API 目前無法存取（被 Cloudflare 阻擋）。\n請至 https://platform.minimaxi.com/user-center/payment/coding-plan 查看額度。",
      };
    }
    return { success: false, error: t.minimaxApiError(resp.status, text) };
  }

  let data: MiniMaxRemainsResponse;
  try {
    data = (await resp.json()) as MiniMaxRemainsResponse;
  } catch (err) {
    return { success: false, error: `MiniMax: JSON 解析失敗: ${err instanceof Error ? err.message : String(err)}` };
  }

  const item = data.model_remains?.[0];
  if (!item) {
    return { success: true, output: t.noQuotaData };
  }

  const total = item.current_interval_total_count ?? 0;
  const used = item.current_interval_usage_count ?? 0;
  const remainPercent = total > 0 ? Math.round(((total - used) / total) * 100) : 0;

  const remainsTimeRaw = item.remains_time ?? 0;
  const resetIn = remainsTimeRaw ? formatDuration(normalizeRemainsSeconds(remainsTimeRaw)) : t.unknown;

  const bar = createProgressBar(remainPercent);
  const lines: string[] = [];
  lines.push(`${t.account} ${maskString(apiKey)} (${sourceKey ?? t.unknown})`);
  lines.push("");
  lines.push(t.promptsLimit5h);
  lines.push(`${bar} ${t.remaining(remainPercent)}`);
  lines.push(`${t.used}: ${used} / ${total || t.unknown}`);
  lines.push(t.resetIn(resetIn));
  if (item.model_name) lines.push(`Model: ${item.model_name}`);

  return { success: true, output: lines.join("\n") };
}
