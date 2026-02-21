import { type Plugin, tool } from "@opencode-ai/plugin";
import { readFile } from "fs/promises";
import { homedir } from "os";
import { join } from "path";
import { t } from "./lib/i18n";
import { queryOpenAIUsage } from "./lib/openai";
import { queryZaiUsage, queryZhipuUsage } from "./lib/zhipu";
import { queryCopilotUsage } from "./lib/copilot";
import { queryMiniMaxUsageFromAuth } from "./lib/minimax";

export const MyQuotaPlugin: Plugin = async () => {
  return {
    tool: {
      myquota: tool({
        description:
          "Query all AI account quota (GitHub Copilot, OpenAI, Z.ai, MiniMax). Returns remaining quota percentages, usage stats, and reset countdowns with visual progress bars.",
        args: {},
        async execute() {
          const authPath = join(homedir(), ".local/share/opencode/auth.json");
          let authData;
          try {
            const content = await readFile(authPath, "utf-8");
            authData = JSON.parse(content);
          } catch (err) {
            return t.authError(authPath, err instanceof Error ? err.message : String(err));
          }

          const [copilotResult, openaiResult, zhipuResult, zaiResult, minimaxResult] = await Promise.all([
            queryCopilotUsage(authData["github-copilot"]),
            queryOpenAIUsage(authData.openai),
            queryZhipuUsage(authData["zhipuai-coding-plan"]),
            queryZaiUsage(authData["zai-coding-plan"]),
            queryMiniMaxUsageFromAuth(authData),
          ]);

          const results: string[] = [];
          const errors: string[] = [];

          collectResult(copilotResult, t.copilotTitle, results, errors);
          collectResult(openaiResult, t.openaiTitle, results, errors);
          collectResult(zhipuResult, t.zhipuTitle, results, errors);
          collectResult(zaiResult, t.zaiTitle, results, errors);
          collectResult(minimaxResult, t.minimaxTitle, results, errors);

          if (results.length === 0 && errors.length === 0) {
            return t.noAccounts;
          }

          let output = results.join("\n");
          if (errors.length > 0) {
            if (output) output += "\n\n";
            output += t.queryFailed + errors.join("\n");
          }

          return output;
        },
      }),
    },
  };
};

function collectResult(result: any, title: string, results: string[], errors: string[]): void {
  if (!result) return;
  if (result.success && result.output) {
    if (results.length > 0) results.push("");
    results.push(title);
    results.push("");
    results.push(result.output);
  } else if (result.error) {
    errors.push(result.error);
  }
}
