/**
 * OpenCode MiniMax quota plugin
 *
 * [Input]: ~/.local/share/opencode/auth.json
 * [Output]: Taiwan Traditional Chinese quota view with █░ progress bars
 *
 * [Tool]: myminimax
 * [Command]: /myminimax (see command/myminimax.md)
 */
import { type Plugin, tool } from "@opencode-ai/plugin";
import { t } from "./lib/i18n";
import { queryMiniMaxUsage } from "./lib/minimax";

export const MyMiniMaxPlugin: Plugin = async () => {
  return {
    tool: {
      myminimax: tool({
        description:
          "Query MiniMax Coding Plan quota (remains). Reads OpenCode auth.json and prints remaining percent, usage and reset countdown with █░ progress bars.",
        args: {},
        async execute() {
          const result = await queryMiniMaxUsage();
          if (!result) return t.noAccounts;

          const results: string[] = [];
          const errors: string[] = [];

          collectResult(result, t.minimaxTitle, results, errors);

          if (results.length === 0 && errors.length === 0) return t.noAccounts;

          let output = results.join("\n");
          if (errors.length > 0) {
            if (output) output += "\n\n";
            output += "❌ 查詢失敗:\n" + errors.join("\n");
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
