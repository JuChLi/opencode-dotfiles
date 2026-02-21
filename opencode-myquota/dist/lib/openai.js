import { t } from "./i18n";
import { formatDuration, createProgressBar, calcRemainPercent, fetchWithTimeout } from "./utils";
function base64UrlDecode(input) {
    const base64 = input.replace(/-/g, "+").replace(/_/g, "/");
    const padLen = (4 - (base64.length % 4)) % 4;
    const padded = base64 + "=".repeat(padLen);
    return Buffer.from(padded, "base64").toString("utf8");
}
function parseJwt(token) {
    try {
        const parts = token.split(".");
        if (parts.length !== 3)
            return null;
        const payloadJson = base64UrlDecode(parts[1]);
        return JSON.parse(payloadJson);
    }
    catch {
        return null;
    }
}
function getEmailFromJwt(token) {
    const payload = parseJwt(token);
    return payload?.["https://api.openai.com/profile"]?.email ?? null;
}
function getAccountIdFromJwt(token) {
    const payload = parseJwt(token);
    return payload?.["https://api.openai.com/auth"]?.chatgpt_account_id ?? null;
}
function formatWindowName(seconds) {
    const days = Math.round(seconds / 86400);
    if (days >= 1) {
        return t.dayLimit(days);
    }
    return t.hourLimit(Math.round(seconds / 3600));
}
function formatWindow(window) {
    const windowName = formatWindowName(window.limit_window_seconds);
    const remainPercent = calcRemainPercent(window.used_percent);
    const progressBar = createProgressBar(remainPercent);
    const resetTime = formatDuration(window.reset_after_seconds);
    return [windowName, `${progressBar} ${t.remaining(remainPercent)}`, t.resetIn(resetTime)];
}
const OPENAI_USAGE_URL = "https://chatgpt.com/backend-api/wham/usage";
async function fetchOpenAIUsage(accessToken) {
    const headers = {
        Authorization: `Bearer ${accessToken}`,
        "User-Agent": "OpenCode-Status-Plugin/1.0",
    };
    const accountId = getAccountIdFromJwt(accessToken);
    if (accountId) {
        headers["ChatGPT-Account-Id"] = accountId;
    }
    const response = await fetchWithTimeout(OPENAI_USAGE_URL, { headers });
    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(t.apiError(response.status, errorText));
    }
    return response.json();
}
function formatOpenAIUsage(data, email) {
    const { plan_type, rate_limit } = data;
    const lines = [];
    const accountDisplay = email || t.unknown;
    lines.push(`${t.account}        ${accountDisplay} (${plan_type})`);
    lines.push("");
    if (rate_limit?.primary_window) {
        lines.push(...formatWindow(rate_limit.primary_window));
    }
    if (rate_limit?.secondary_window) {
        lines.push("");
        lines.push(...formatWindow(rate_limit.secondary_window));
    }
    if (rate_limit?.limit_reached) {
        lines.push("");
        lines.push(t.limitReached);
    }
    return lines.join("\n");
}
export async function queryOpenAIUsage(authData) {
    if (!authData || authData.type !== "oauth" || !authData.access) {
        return null;
    }
    if (authData.expires && authData.expires < Date.now()) {
        return {
            success: false,
            error: t.tokenExpired,
        };
    }
    try {
        const email = getEmailFromJwt(authData.access);
        const usage = await fetchOpenAIUsage(authData.access);
        return {
            success: true,
            output: formatOpenAIUsage(usage, email),
        };
    }
    catch (err) {
        return {
            success: false,
            error: err instanceof Error ? err.message : String(err),
        };
    }
}
//# sourceMappingURL=openai.js.map