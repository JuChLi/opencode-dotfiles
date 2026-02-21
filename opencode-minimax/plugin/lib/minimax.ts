import { t } from "./i18n";
import type { QueryResult } from "./types";
import { createProgressBar, fetchWithTimeout, formatDuration, maskString, normalizeRemainsSeconds } from "./utils";
import { extractApiKey, extractGroupId, extractMiniMaxNode, loadAuthData } from "./auth";

type MiniMaxRemainsResponse = {
  model_remains?: Array<{
    model_name?: string;
    current_interval_total_count?: number;
    current_interval_usage_count?: number;
    remains_time?: number;
  }>;
};

export async function queryMiniMaxUsage(): Promise<QueryResult | null> {
  // 1) Read auth.json
  const { authPath, auth, error } = await loadAuthData();
  if (error || !auth) {
    return { success: false, error: t.authError(authPath, error ?? "unknown") };
  }

  // 2) Get minimax node + key/groupId
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

  // 3) Call API
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
  lines.push(`${t.promptsLimit5h}`);
  lines.push(`${bar} ${t.remaining(remainPercent)}`);
  lines.push(`${t.used}: ${used} / ${total || t.unknown}`);
  lines.push(t.resetIn(resetIn));
  if (item.model_name) lines.push(`Model: ${item.model_name}`);

  return { success: true, output: lines.join("\n") };
}
