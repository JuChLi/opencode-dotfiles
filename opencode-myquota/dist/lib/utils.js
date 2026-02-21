import { t, currentLang } from "./i18n";
import { REQUEST_TIMEOUT_MS } from "./types";
export function formatDuration(seconds) {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const parts = [];
    if (days > 0)
        parts.push(t.days(days));
    if (hours > 0)
        parts.push(t.hours(hours));
    if (minutes > 0 || parts.length === 0)
        parts.push(t.minutes(minutes));
    return parts.join(currentLang === "en" ? " " : "");
}
export function createProgressBar(remainPercent, width = 30) {
    const safePercent = Math.max(0, Math.min(100, remainPercent));
    const filled = Math.round((safePercent / 100) * width);
    const empty = width - filled;
    return "█".repeat(filled) + "░".repeat(empty);
}
export function calcRemainPercent(usedPercent) {
    return Math.round(100 - usedPercent);
}
export function formatTokens(tokens) {
    return (tokens / 1000000).toFixed(1) + "M";
}
export async function fetchWithTimeout(url, options, timeoutMs = REQUEST_TIMEOUT_MS) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    try {
        const response = await fetch(url, { ...options, signal: controller.signal });
        return response;
    }
    catch (err) {
        if (err instanceof Error && err.name === "AbortError") {
            throw new Error(t.timeoutError(Math.round(timeoutMs / 1000)));
        }
        throw err;
    }
    finally {
        clearTimeout(timeoutId);
    }
}
export function safeMax(arr) {
    if (arr.length === 0)
        return 0;
    return Math.max(...arr);
}
export function maskString(str, showChars = 4) {
    if (str.length <= showChars * 2)
        return str;
    return `${str.slice(0, showChars)}****${str.slice(-showChars)}`;
}
export function normalizeRemainsSeconds(remainsTime) {
    if (!Number.isFinite(remainsTime) || remainsTime <= 0)
        return 0;
    return remainsTime > 100000 ? Math.round(remainsTime / 1000) : Math.round(remainsTime);
}
//# sourceMappingURL=utils.js.map