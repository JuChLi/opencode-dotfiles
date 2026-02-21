import { readFile } from "fs/promises";
import { homedir } from "os";
import { join } from "path";
export async function loadAuthData() {
    const authPath = join(homedir(), ".local/share/opencode/auth.json");
    try {
        const content = await readFile(authPath, "utf-8");
        const auth = JSON.parse(content);
        return { authPath, auth };
    }
    catch (err) {
        return { authPath, error: err instanceof Error ? err.message : String(err) };
    }
}
export function extractMiniMaxNode(auth) {
    if (!auth)
        return {};
    const primary = auth["minimax-coding-plan"];
    if (primary)
        return { node: primary, sourceKey: "minimax-coding-plan" };
    const secondary = auth.minimax;
    if (secondary)
        return { node: secondary, sourceKey: "minimax" };
    return {};
}
export function extractApiKey(node) {
    if (!node)
        return undefined;
    const k = node.key ?? node.api_key ?? node.token;
    return typeof k === "string" && k.trim() ? k.trim() : undefined;
}
export function extractGroupId(node) {
    if (!node)
        return undefined;
    const g = node.groupId ?? node.GroupId ?? node.group_id ?? node.groupID ?? node.group;
    return typeof g === "string" && g.trim() ? g.trim() : undefined;
}
//# sourceMappingURL=auth.js.map